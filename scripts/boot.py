# This file is executed on every boot (including wake-boot from deepsleep)

import esp, gc, webrepl, network
import usocket as socket
esp.osdebug(None) #turn off vendor O/S debugging messages
webrepl.start()
gc.collect()

from config import *

# -------------------------------------------------------------------
# configuration consts
# -------------------------------------------------------------------
CONFIG_WIFI_SSID = 'PROJECT_X'
CONFIG_WIFI_PASSWORD = 'P4prykowe'
CONFIG_SERVER_PORT = 80
CONFIG_HTML_INDEX = 'config_index.html'
FLASH_BUTTON_PIN = 0
CONFIG_DELAY = 3
REBOOT_DELAY = 3



# -------------------------------------------------------------------
# aux functions
# -------------------------------------------------------------------

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


config_mode = False

print('\nReading config file...')
read_err = read_config()
if read_err != 0:
    print('Forcing config mode.')
    config_mode = True


from machine import Pin

led = Pin(2, Pin.OUT)


access_point_start()
server_start()

print('\n### Quitting boot.py ###')