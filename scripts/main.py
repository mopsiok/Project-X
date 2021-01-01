# This file is executed after boot.py

import network, machine, webrepl, sys, ubinascii, utime

import config
from umqttsimple import MQTTClient

# running webrepl in case boot.py crashed
webrepl.start()



# -------------------------------------------------------------------
# configuration
# -------------------------------------------------------------------

RELAY_PIN = 2

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

# TODO description
def wifi_connect(ssid, password, timeout=10000):
    print('\nConnecting WiFi (%s,%s)...' % (ssid, password))
    sta = network.WLAN(network.STA_IF)
    if (not ssid) or (not password):
        sta.active(False)
        return 1
    
    # disable access point mode
    network.WLAN(network.AP_IF).active(False)

    sta.active(True)
    sta.connect(ssid, password)
    while not sta.isconnected():
        utime.sleep_ms(10)
        timeout -= 10
        if timeout <= 0:
            print('Connection timeout.')
            return 2
    print('Connected:', sta.ifconfig())
    return 0

# TODO description
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
        print(e) # sys.print_exception(e)
        return 2
        


# -------------------------------------------------------------------
# main program
# -------------------------------------------------------------------  

print('\n\n### Entering main.py ###')

#reading boot and main configs
config.boot_read()
config.main_read()
CONFIG = config.MAIN_CONFIG
CONFIG_BOOT = config.BOOT_CONFIG

# defining GPIOs
relay = machine.Pin(RELAY_PIN, machine.Pin.OUT)

# connecting to WiFi
ssid = CONFIG_BOOT.get('WIFI_SSID')
password = CONFIG_BOOT.get('WIFI_PASS')
wifi_connect(ssid, password)

#TODO to be deleted
for i in range(5):
    relay.off()
    utime.sleep_ms(250)
    relay.on()
    utime.sleep_ms(250)
    
    mqtt_publish(22+i*0.5, 70+i)
    utime.sleep(30)

print('### Quitting main.py ###')