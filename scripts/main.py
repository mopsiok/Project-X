# This file is executed after boot.py

import network, time, machine, webrepl

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
        time.sleep_ms(10)
        timeout -= 10
        if timeout <= 0:
            print('Connection timeout.')
            return 2
    print('Connected:', sta.ifconfig())
    return 0

# TODO description
def send_data(temperature, humidity):
    print("\n\n\n\n")
    print(CONFIG)
    server = CONFIG.get('MQTT_SERVER')
    channel_id = CONFIG.get('MQTT_CHANNEL_ID')
    key = CONFIG.get('MQTT_WRITE_KEY')
    print(server, channel_id, key)
    
    if (not server) or (not channel_id) or (not key):
        print('Missing MQTT config, sending data skipped')
        return 1

    try:
        topic = "channels/" + channel_id + "/publish/" + key
        print(topic)
        payload = 'field1=%.2f&field2=%.2f' % (temperature, humidity)
        print(payload)
        client = MQTTClient("umqtt_client", server)
        client.connect()
        client.publish(topic, payload)
        client.disconnect()

        print('Message published (%.2f*C, %.2f%)' % (temperature, humidity))
        return 0
    except Exception as e:
        print(e)
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
for i in range(1):
    relay.off()
    time.sleep_ms(250)
    relay.on()
    time.sleep_ms(250)
    
    send_data(22+i*0.5, 70+i)
    time.sleep(30)

print('### Quitting main.py ###')