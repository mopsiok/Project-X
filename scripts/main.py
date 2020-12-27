import network, time, machine
try:
    import usocket as socket
except:
    import socket
import ussl as ssl

from config import *
from templates import *
from umqttsimple import MQTTClient

# -------------------------------------------------------------------
# configuration
# -------------------------------------------------------------------

RELAY_PIN = 2



# -------------------------------------------------------------------
# aux functions
# -------------------------------------------------------------------

def wifi_connect(ssid, password, timeout=10000):
    sta = network.WLAN(network.STA_IF)

    if (not ssid) or (not password):
        sta.active(False)
        return 1;
    
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


def send_data(temperature, humidity):
    server = CONFIG.get('MQTT_SERVER')
    channel_id = CONFIG.get('MQTT_CHANNEL_ID')
    key = CONFIG.get('MQTT_WRITE_KEY')
    
    if (not server) or (not channel_id) or (not key):
        print('Missing MQTT config, sending data skipped')
        return 1

    try:
        topic = "channels/" + channel_id + "/publish/" + key
        payload = 'field1=%.2f&field2=%.2f' % (temperature, humidity)
        client = MQTTClient("umqtt_client", server)
        client.connect()
        client.publish(topic, payload)
        client.disconnect()

        print('Message published')
        return 0
    except:
        print('Connection error')
        return 2
        


# -------------------------------------------------------------------
# main program
# -------------------------------------------------------------------  

print('\n\n### Entering main.py ###')
print('\nReading config file...')
read_config()

# defining GPIOs
relay = machine.Pin(RELAY_PIN, machine.Pin.OUT)

# connecting to WiFi
ssid = CONFIG.get('WIFI_SSID')
password = CONFIG.get('WIFI_PASS')
print('\nConnecting WiFi (%s,%s)...' % (ssid, password))
wifi_connect(ssid, password)

#TODO to be deleted
for i in range(10):
    relay.off()
    time.sleep_ms(250)
    relay.on()
    time.sleep_ms(250)
    
    send_data(22+i*0.5, 70+i)
    time.sleep(30)

print('### Quitting main.py ###')