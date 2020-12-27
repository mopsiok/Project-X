import socket, time, machine
from umqtt.simple import MQTTClient
from math import sin

#konfiguracja
RELAY_GPIO = 2
SERVER = "mqtt.thingspeak.com"
CHANNEL_ID = "1269906"
WRITE_API_KEY = "GAWE54HV7OIWIAMI"
PUBLISH_PERIOD = 20


####################################################################	
print('main.py')

relay = machine.Pin(RELAY_GPIO, machine.Pin.OUT)
client = MQTTClient("umqtt_client", SERVER)
topic = "channels/" + CHANNEL_ID + "/publish/" + WRITE_API_KEY

i = 0
while True:
	temp = 23.4 + sin(0.1*i)
	hum = 75 + 5*sin(0.1*(i+5))
	payload = "field1=%.1f&field2=%.1f" % (temp, hum)

	relay.off()
	client.connect()
	client.publish(topic, payload)
	client.disconnect()
	relay.on()

	time.sleep(PUBLISH_PERIOD)
	i += 1