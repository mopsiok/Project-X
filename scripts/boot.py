# This file is executed on every boot (including wake-boot from deepsleep)

import esp, gc, webrepl, network, machine, utime
from machine import Pin
import usocket as socket #TODO TBD

import config

esp.osdebug(None) #turn off vendor O/S debugging messages
webrepl.start()
gc.collect()



# -------------------------------------------------------------------
# configuration & consts
# -------------------------------------------------------------------

AP_SSID = 'PROJECT_X'
AP_PASSWORD = 'P4prykowe'

SERVER_INDEX = 'boot_index.html'
SERVER_PORT = 80

CONFIG = {}

# magic numbers
BOOT_BUTTON_PIN = 0 # boot button gpio (flash pin)
BOOT_ENTER_DELAY = 3000 # waiting period before checking button status, in ms

LED_PIN = 2



# -------------------------------------------------------------------
# aux functions
# -------------------------------------------------------------------

def led_on():
    global led
    led.off()

def led_off():
    global led
    led.on()

# start wifi access point
def access_point_start():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=CONFIG_WIFI_SSID, password=CONFIG_WIFI_PASSWORD, authmode=network.AUTH_WPA2_PSK)
    print('Access Point started (%s,%s)' % (CONFIG_WIFI_SSID,CONFIG_WIFI_PASSWORD))


# send a response (webpage) to the user
def server_respond():
    try:
        f = open(CONFIG_HTML_INDEX)
        html = f.read()
        html = html % (CONFIG.get('WIFI_SSID'), CONFIG.get('WIFI_PASS'))
    finally:
        f.close()

    return html


# execute data received from user
def server_process_data(data):
    #TODO funkcja wykonujaca data + zwracajaca czy wyjsc z serwera (po kliknieciu guzika zamknij)
    pass


# run a local webserver for user configuration
def server_start():
    try:
        s = socket.socket()
        ai = socket.getaddrinfo('0.0.0.0',CONFIG_SERVER_PORT)
        addr = ai[0][-1]
        s.bind(addr)
        s.listen(1)
        print('Configuration server started on 192.168.4.1:%d' % CONFIG_SERVER_PORT)

        for i in range(5):
            try:
                conn, addr = s.accept()
                print('Connection from %s' % str(addr))
                request = conn.recv(1024)
                request = request.decode() #bytes to string

                data = {}

                try:
                    pos1 = request.find('GET /?')
                    if pos1 >= 0:
                        #request has GET data sent from the user - parse
                        pos2 = request.find(' HTTP')
                        request = request[pos1+6 : pos2]
                    
                        for field in request.split('&'):
                            k, v = field.split('=')
                            data[k] = v
                except Exception as e:
                    print(e)
                    
                print('GET data:', data)
                server_process_data(data)

                #TODO zmienic for na while i wychodzic zwrotka z server_process_data
                
                conn.send(server_respond())
                conn.close()
            except Exception as e:
                print(e)
    except Exception as e: 
        print(e)


# # reboot the board after some delay
# def reboot():
#     import time
#     import machine
#     print('rebooting ...')
#     time.sleep(REBOOT_DELAY)
#     machine.reset()



# -------------------------------------------------------------------
# main program
# -------------------------------------------------------------------  

print('\n\n### Entering boot.py ###')

led = Pin(LED_PIN, Pin.OUT)
button = Pin(BOOT_BUTTON_PIN, Pin.IN, Pin.PULL_UP)

led_off()

#reading boot config
err = config.boot_read()
CONFIG = config.BOOT_CONFIG 
config_mode = False
if err != 0:
    print('Forcing config mode.')
    config_mode = True

# checking FLASH button for specifying configuration mode
if not config_mode:
    for i in range(30):
        utime.sleep_ms(int(BOOT_ENTER_DELAY/30))
        if (i % 2 == 1):
            led_on()
        else:
            led_off()

    if (button.value() == 0):
        config_mode = True

# entering config mode
if config_mode:
    print('\n[CONFIG MODE]')
    led_on()

    utime.sleep(1)
    #access_point_start()
    #server_start()
else:
    print('\n[NORMAL MODE]')

led_off()

print('\n### Quitting boot.py ###')