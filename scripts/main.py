# This file is executed after boot.py

import gc
from umqtt.simple import MQTTClient
gc.collect()
import config
gc.collect()
import webserver
gc.collect()
import network
gc.collect()
import machine
gc.collect()
import ubinascii
gc.collect()
import utime
gc.collect()
import sys #TBD
gc.collect()



# -------------------------------------------------------------------
# configuration and magic numbers
# -------------------------------------------------------------------

SERVER_INDEX = 'main_index.html'

# gpio definitions
RELAY_PIN = 5           # light relay
SENSOR_PIN = 4          # DHT sensor
PWM_PINS = [0,2,14,15]  # PWM for fans 1..4
SCL_PIN = 12            # aux I2C clock
SDA_PIN = 13            # aux I2C data

# possible webserver responses
SERVER_PROCESS_EMPTY = 0
SERVER_PROCESS_SAVE = 1
SERVER_PROCESS_INCOMPLETE = 2
SERVER_PROCESS_ERROR = 254
SERVER_PROCESS_REBOOT = 255

CONFIG = {} 
CONFIG_BOOT = {}



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


# -------------------------------------------------------------------
# wifi-related functions
# -------------------------------------------------------------------

# connect to a WiFi network
# ssid - string
# password - string
# timeout - int, maximum timeout in ms
# returns error code (0 = connected; 1 = missing credentials; 2 = timeout) and configuration info
def wifi_connect(ssid, password, timeout=10000):
    print('\nConnecting WiFi (%s,%s)...' % (ssid, password))
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


# open a socket to MQTT broker, send data and close the socket
# temperature - float, in *C
# humidity - float, in %
# returns error code (0 = ok, 1 = wrong MQTT config; 2 = general error)
def mqtt_publish(temperature, humidity):
    server = CONFIG.get('MQTT_SERVER')
    channel_id = CONFIG.get('MQTT_CHANNEL_ID')
    key = CONFIG.get('MQTT_WRITE_KEY')    
    if (not server) or (not channel_id) or (not key):
        print('Missing MQTT config, sending data skipped')
        return 1

    try:
        client_id = aux_generate_id()
        topic = "channels/" + channel_id + "/publish/" + key
        payload = 'field1=%.2f&field2=%.2f' % (temperature, humidity)
        client = MQTTClient(client_id, server)
        client.connect()
        client.publish(topic, payload)
        client.disconnect()

        print('Message published (%.2f*C, %.2f%%)' % (temperature, humidity))
        return 0
    except Exception as e:
        sys.print_exception(e)
        return 2
        


# -------------------------------------------------------------------
# webserver
# -------------------------------------------------------------------

# execute data received from user (if 255 returned, the server will stop)
def server_process_data(data):
    print("\nReceived data:")
    print(data)


# response webpage to be returned to the user
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


    data = (CONFIG.get('LIGHT_ON'), CONFIG.get('LIGHT_OFF'), \
        CONFIG.get('PWM1_DAY'), CONFIG.get('PWM1_NIGHT'), CONFIG.get('PWM2_DAY'), CONFIG.get('PWM2_NIGHT'),
        CONFIG.get('PWM3_DAY'), CONFIG.get('PWM3_NIGHT'), CONFIG.get('PWM4_DAY'), CONFIG.get('PWM4_NIGHT'),
        CONFIG.get('MQTT_SERVER'), CONFIG.get('MQTT_CHANNEL_ID'), CONFIG.get('MQTT_WRITE_KEY'), CONFIG.get('MQTT_PUBLISH_PERIOD'),
        info)

    webserver.send_webpage(data)




# -------------------------------------------------------------------
# main program
# -------------------------------------------------------------------  

print('\n\n### Entering main.py ###')

#reading boot and main configs
config.boot_read()
config.main_read()
CONFIG = config.MAIN_CONFIG
CONFIG_BOOT = config.BOOT_CONFIG

#defining GPIOs
relay = machine.Pin(RELAY_PIN, machine.Pin.OUT)

#connecting to WiFi
ssid = CONFIG_BOOT.get('WIFI_SSID')
password = CONFIG_BOOT.get('WIFI_PASS')
wifi_err, network_info = wifi_connect(ssid, password)
ip = network_info[0]

#starting webserver
webserver.start(ip, 80, SERVER_INDEX, server_process_data, server_respond)

#TODO wywalic load_webpage i respond do modulu, w funkcji uruchamiania podawac jakas analogie dla data zeby z zewnatrz nie trzeba bylo 
# !! albo zrobic funkcje pomocnicza ktora uwzglednia tylko load_webpage i obsluge globalnych tablic, i jest wykonywana z poziomu respond na zasadzie generate_webpage(data)
# wywalic WEBPAGE_CODE

#TODO change webpage display in boot.py (NOT COMPATIBLE with current webserver.py)

#TODO to be deleted
for i in range(2):
    relay.off()
    utime.sleep_ms(250)
    relay.on()
    utime.sleep_ms(250)
    
    #mqtt_publish(22+i*0.5, 70+i)
    #utime.sleep(30)

print('### Quitting main.py ###')