# This file is executed on every boot (including wake-boot from deepsleep)

# configuration
WIFI_SSID = "UPC865E232"
WIFI_PASS = "RM4yvcnxjurh"

import esp
esp.osdebug(None) #turn off vendor O/S debugging messages

#domyslne
import gc
import webrepl
webrepl.start()
gc.collect()

#wylaczenie trybu AP i polaczenie z istniejaca siecia
print('\n\nConnecting...')
import network, time, machine
network.WLAN(network.AP_IF).active(False)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(WIFI_SSID,WIFI_PASS)
count = 0
while not sta_if.isconnected():
	time.sleep_ms(1)
	count += 1
	if count==10000:
		print('Connection timeout.')
		break
print('Connected: ', sta_if.ifconfig(), '\n')