# This file is executed after boot.py

import gc
from umqtt.simple import MQTTClient
import config, timing, BSP
gc.collect()
import network, machine, ubinascii, utime, micropython
gc.collect()



# -------------------------------------------------------------------
# configuration and magic numbers
# -------------------------------------------------------------------

# configuration dictionary
CONFIG = {} 



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
    print('Rebooting...')
    machine.reset()


# reads config file to global CONFIG and returns error code
def config_read():
    print('Reading config file.')
    err = config.read(CONFIG)
    print(CONFIG)
    return err


# writes global CONFIG to config file and returns error code
def config_write():
    print('Writing config file.')
    err = config.write(CONFIG)
    return err



# -------------------------------------------------------------------
# wifi-related functions
# -------------------------------------------------------------------

# connect to a WiFi network
# ssid:     string
# password: string
# timeout:  int, maximum timeout in ms
# returns:  error code (0 = connected; 1 = missing credentials; 2 = timeout) and configuration info
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
# main application timer, executed once in a second
# -------------------------------------------------------------------

timer_presc = [0,0,0]
timer_hardware_flag = False
timer_sensor_flag = False
timer_mqtt_flag = False
timer_ntp_flag = False
timer_gc_flag = False
timer_meminfo_flag = False
def main_timer_callback(tim):
    global timer_presc, timer_hardware_flag, timer_sensor_flag, timer_mqtt_flag, timer_ntp_flag, timer_gc_flag, timer_meminfo_flag
    for i in range(len(timer_presc)):
        timer_presc[i] += 1
    
    timer_hardware_flag = True
    timer_gc_flag = True

    if timer_presc[0] >= 5:
        timer_presc[0] = 0
        timer_sensor_flag = True

    if timer_presc[1] >= 60:
        timer_presc[1] = 0
        timer_mqtt_flag = True
        timer_ntp_flag = True

    if timer_presc[2] >= 10:
        timer_presc[2] = 0
        timer_meminfo_flag = True


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
# main program
# -------------------------------------------------------------------  

print('\n\n### Entering main.py ###')


#reading config
err = config_read()

#connecting to WiFi
err, network_info = wifi_connect(CONFIG.get('WIFI_SSID'), CONFIG.get('WIFI_PASS'))
ip = network_info[0]

#getting time
err = timing.ntp_synchronize()
print("Synchronized to %i.%02i.%02i %02i:%02i:%02i" % timing.get_datetime())

#initialize hardware
BSP.init_all()

#set up a 1Hz timer for main application
timer = machine.Timer(-1)
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=main_timer_callback)

while True:
    try:
        #updating hardware
        if timer_hardware_flag:
            timer_hardware_flag = False
            day_flag = timing.check_day_mode(CONFIG['LIGHT_ON'], CONFIG['LIGHT_OFF'])
            update_hardware(day_flag)

            h,m,s = timing.get_time()
            print('%02i:%02i:%02i - %s' % (h, m, s, ('DAY TIME' if day_flag else 'NIGHT TIME')))

        #reading the sensor
        if timer_sensor_flag:
            timer_sensor_flag = False
            temp, hum = BSP.sensor_measure()
            print('Sensor: %04.1f*C, %04.1f%%' % (temp, hum))
        
        #sending data to MQTT broker
        if timer_mqtt_flag:
            timer_mqtt_flag = False
            temp, hum = BSP.sensor_get_average()
            mqtt_publish(temp, hum)

        #time synchronization
        if timer_ntp_flag:
            timer_ntp_flag = False
            if timing.ntp_synchronize() == 0:
                print('NTP synchronization completed.')

        #garbage collector
        if timer_gc_flag:
            timer_gc_flag = False
            gc.collect()
            gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

        #memory info
        if timer_meminfo_flag:
            timer_meminfo_flag = False
            micropython.mem_info()

    except Exception as e:
        print(e)

#unhandled error occured - rebooting
print('Gone outside of main loop!')
esp_reboot()

print('### Quitting main.py ###')