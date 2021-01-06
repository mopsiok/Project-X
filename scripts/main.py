# This file is executed after boot.py

import gc
from umqtt.simple import MQTTClient
import config, webserver, timing, BSP
gc.collect()
import network, machine, ubinascii, utime
gc.collect()



# -------------------------------------------------------------------
# configuration and magic numbers
# -------------------------------------------------------------------

# configuration index file
SERVER_INDEX = 'main_index.html'

# possible webserver responses
SERVER_PROCESS_EMPTY = 0
SERVER_PROCESS_SAVE = 1
SERVER_PROCESS_ERROR = 254
SERVER_PROCESS_REBOOT = 255

# configuration dictionaries - for main and boot config
CONFIG = {} 
CONFIG_BOOT = {}


# -------------------------------------------------------------------
# main application timer, executed once in a second
# -------------------------------------------------------------------

timer_presc = [0,0]
def main_timer_callback(tim):
    global timer_presc
    for i in range(len(timer_presc)):
        timer_presc[i] += 1
    
    day_flag = timing.check_day_mode(CONFIG['LIGHT_ON'], CONFIG['LIGHT_OFF'])
    update_hardware(day_flag)

    #h,m,s = timing.get_time()
    #print('%02i:%02i:%02i - %s' % (h, m, s, ('DAY TIME' if day_flag else 'NIGHT TIME')))

    #reading the sensor
    if timer_presc[0] >= 5:
        timer_presc[0] = 0
        #TODO read sensor and re-calculate average

    #send measurements and synchronize time
    if timer_presc[1] >= 60:
        timer_presc[1] = 0

        #TODO read moving average and publish it
        #mqtt_publish(22+i*0.5, 70+i)

        timing.ntp_synchronize()

    #garbage collector
    gc.collect()
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())


# set relay and fans according to current time
# day_flag: True = day; False - night
def update_hardware(day_flag):
    if day_flag:
        BSP.relay_on()
        BSP.fan_set(0, int(CONFIG['PWM1_DAY']))
        BSP.fan_set(1, int(CONFIG['PWM2_DAY']))
        BSP.fan_set(2, int(CONFIG['PWM3_DAY']))
        BSP.fan_set(3, int(CONFIG['PWM4_DAY']))
    else:
        BSP.relay_off()
        BSP.fan_set(0, int(CONFIG['PWM1_NIGHT']))
        BSP.fan_set(1, int(CONFIG['PWM2_NIGHT']))
        BSP.fan_set(2, int(CONFIG['PWM3_NIGHT']))
        BSP.fan_set(3, int(CONFIG['PWM4_NIGHT']))



# -------------------------------------------------------------------
# aux functions
# -------------------------------------------------------------------

# get a string based on module's unique ID
def aux_get_id():
    id_str = ubinascii.hexlify(machine.unique_id())
    return id_str.decode()


# generate a pseudo-random string based on module's unique ID and current time
def aux_generate_id():
    return "%s_%04i" % (aux_get_id(), (utime.ticks_us() % 10000))


# reboot the board
def esp_reboot():
    print('Rebooting ...')
    machine.reset()



# -------------------------------------------------------------------
# wifi-related functions
# -------------------------------------------------------------------

# connect to a WiFi network
# ssid - string
# password - string
# timeout - int, maximum timeout in ms
# returns error code (0 = connected; 1 = missing credentials; 2 = timeout) and configuration info
def wifi_connect(ssid, password, timeout=10000):
    print('Connecting to WiFi (%s,%s)...' % (ssid, password))
    sta = network.WLAN(network.STA_IF)
    if (not ssid) or (not password):
        sta.active(False)
        return (1, sta.ifconfig())
    
    # disable access point mode
    network.WLAN(network.AP_IF).active(False)

    sta.active(True)
    sta.connect(ssid, password)
    while not sta.isconnected():
        utime.sleep_ms(10)
        timeout -= 10
        if timeout <= 0:
            print('Connection timeout.')
            return (2, sta.ifconfig())
    info = sta.ifconfig()
    print('Connected:', info)
    return (0, info)


# disconnect from a WiFi network
def wifi_disconnect():
    print('Disconnecting from WiFi...')
    sta = network.WLAN(network.STA_IF)
    sta.disconnect()


# open a socket to MQTT broker, send data and close the socket
# temperature - float, in *C
# humidity - float, in %
# returns error code (0 = ok, 1 = wrong MQTT config; 2 = general error)
def mqtt_publish(temperature, humidity):
    server = CONFIG.get('MQTT_SERVER')
    channel_id = CONFIG.get('MQTT_CHANNEL_ID')
    key = CONFIG.get('MQTT_WRITE_KEY')

    if server and channel_id and key:
        try:
            client = MQTTClient(aux_generate_id(), server)
            topic = "channels/" + channel_id + "/publish/" + key
            payload = 'field1=%.2f&field2=%.2f' % (temperature, humidity)
            
            client.connect()
            client.publish(topic, payload)
            print('Message published (%.2f*C, %.2f%%)' % (temperature, humidity))
            result = 0
        except Exception as e:
            print(e) #sys.print_exception(e)
            result = 2
        finally:
            client.disconnect()
    else:
        print('Missing MQTT config, sending data skipped')
        result = 1

    gc.collect()
    return result



# -------------------------------------------------------------------
# webserver
# -------------------------------------------------------------------

# fill the response data list with user data
#   info - string, response message for the user
def server_update_response_data(info):
    webserver.WEBPAGE_INSERT_DATA[0] = CONFIG.get('LIGHT_ON')
    webserver.WEBPAGE_INSERT_DATA[1] = CONFIG.get('LIGHT_OFF')
    webserver.WEBPAGE_INSERT_DATA[2] = CONFIG.get('PWM1_DAY')
    webserver.WEBPAGE_INSERT_DATA[3] = CONFIG.get('PWM1_NIGHT')
    webserver.WEBPAGE_INSERT_DATA[4] = CONFIG.get('PWM2_DAY')
    webserver.WEBPAGE_INSERT_DATA[5] = CONFIG.get('PWM2_NIGHT')
    webserver.WEBPAGE_INSERT_DATA[6] = CONFIG.get('PWM3_DAY')
    webserver.WEBPAGE_INSERT_DATA[7] = CONFIG.get('PWM3_NIGHT')
    webserver.WEBPAGE_INSERT_DATA[8] = CONFIG.get('PWM4_DAY')
    webserver.WEBPAGE_INSERT_DATA[9] = CONFIG.get('PWM4_NIGHT')
    webserver.WEBPAGE_INSERT_DATA[10] = CONFIG.get('MQTT_SERVER')
    webserver.WEBPAGE_INSERT_DATA[11] = CONFIG.get('MQTT_CHANNEL_ID')
    webserver.WEBPAGE_INSERT_DATA[12] = CONFIG.get('MQTT_WRITE_KEY')
    webserver.WEBPAGE_INSERT_DATA[13] = CONFIG.get('MQTT_PUBLISH_PERIOD')
    webserver.WEBPAGE_INSERT_DATA[14] = info


# execute data received from user (if 255 returned, the server will stop)
def server_process_data(data):
    global CONFIG
    try:
        print("Received data:")
        print(data)

        if len(data) == 0:
            return SERVER_PROCESS_EMPTY
        
        if data.get('REBOOT'):
            return SERVER_PROCESS_REBOOT
        else:
            for key in data.keys():
                value = data[key]
                if (key in CONFIG.keys()) and value:
                    CONFIG[key] = value.replace('%3A', ':')
            config.main_write()
            return SERVER_PROCESS_SAVE
    except:
        print('Error while processing user data.')
        return SERVER_PROCESS_ERROR


# response webpage to be returned to the user
# process_result - return code of process callback executing user data
def server_respond(process_result):
    info = ''
    if process_result == SERVER_PROCESS_SAVE:
        info = 'Configuration saved.'
    elif process_result == SERVER_PROCESS_INCOMPLETE:
        info = 'Incomplete data.'
    elif process_result == SERVER_PROCESS_ERROR:
        info = 'Unexpected error.'
    elif process_result == SERVER_PROCESS_REBOOT:
        info = 'Rebooting...'

    server_update_response_data(info)
    webserver.send_webpage()




# -------------------------------------------------------------------
# main program
# -------------------------------------------------------------------  

print('\n\n### Entering main.py ###')

#reading boot and main configs
config.boot_read()
config.main_read()
CONFIG = config.MAIN_CONFIG
CONFIG_BOOT = config.BOOT_CONFIG

#connecting to WiFi
ssid = CONFIG_BOOT.get('WIFI_SSID')
password = CONFIG_BOOT.get('WIFI_PASS')
err, network_info = wifi_connect(ssid, password)
ip = network_info[0]

#getting time
err = timing.ntp_synchronize()
print("Synchronized to %i.%02i.%02i %02i:%02i:%02i" % timing.get_datetime())

#initialize hardware
BSP.init_all()

#set up a 1Hz timer for main application
timer = machine.Timer(-1)
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=main_timer_callback)

#starting config webserver
webserver.start(ip, 80, SERVER_INDEX, server_process_data, server_respond)

#server is stopped on user demand or due to error - rebooting
utime.sleep_ms(200)
#TODO esp_reboot()
    

#TODO to be deleted
# for i in range(2):
#     relay.off()
#     utime.sleep_ms(250)
#     relay.on()
#     utime.sleep_ms(250)
    
#     #mqtt_publish(22+i*0.5, 70+i)
#     #utime.sleep(30)

print('### Quitting main.py ###')