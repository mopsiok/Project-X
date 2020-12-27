import network, time, machine
from config import *

# -------------------------------------------------------------------
# configuration
# -------------------------------------------------------------------

RELAY_PIN = 2
SERVER = "mqtt.thingspeak.com"
CHANNEL_ID = "1269906"
WRITE_API_KEY = "GAWE54HV7OIWIAMI"
PUBLISH_PERIOD = 20



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


# relay = machine.Pin(RELAY_GPIO, machine.Pin.OUT)
# client = MQTTClient("umqtt_client", SERVER)
# topic = "channels/" + CHANNEL_ID + "/publish/" + WRITE_API_KEY

# i = 0
# while True:
#     temp = 23.4 + sin(0.1*i)
#     hum = 75 + 5*sin(0.1*(i+5))
#     payload = "field1=%.1f&field2=%.1f" % (temp, hum)

#     relay.off()
#     client.connect()
#     client.publish(topic, payload)
#     client.disconnect()
#     relay.on()

#     time.sleep(PUBLISH_PERIOD)
#     i += 1

print('### Quitting main.py ###')