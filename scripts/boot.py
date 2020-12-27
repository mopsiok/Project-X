# This file is executed on every boot (including wake-boot from deepsleep)

import esp
esp.osdebug(None) #turn off vendor O/S debugging messages
import gc
import webrepl
webrepl.start()
gc.collect()

print('\n\n### Entering boot.py ###')


from templates import *
CONFIG_WIFI_SSID = 'PROJECT_X'
CONFIG_WIFI_PASSWORD = 'P4prykowe'
CONFIG_SERVER_PORT = 443
FLASH_BUTTON_PIN = 0
CONFIG_DELAY = 3
REBOOT_DELAY = 3

from config import *

# -------------------------------------------------------------------
# configuration server
# based on: github.com/artem-smotrakov/yellow-duck
# -------------------------------------------------------------------

try:
    import usocket as socket
except:
    import socket
import ussl as ssl

INDENT = '    '

# start a web server which asks for wifi ssid/password, and other settings
# it stores settings to a config file
# it's a very simple web server
# it assumes that it's running in safe environment for a short period of time,
# so it doesn't check much input data
#
# based on https://github.com/micropython/micropython/blob/master/examples/network/http_server_ssl.py
def start_local_server(use_stream = True):
    s = socket.socket()

    # binding to all interfaces - server will be accessible to other hosts!
    ai = socket.getaddrinfo('0.0.0.0', CONFIG_SERVER_PORT)
    print('bind address info: ', ai)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print('server started on %s:%d/' % (addr, CONFIG_SERVER_PORT))

    # main server loop
    while True:
        print('waiting for connection ...')
        res = s.accept()

        client_s = res[0]
        client_addr = res[1]

        print("client address: ", client_addr)
        client_s = ssl.wrap_socket(client_s, server_side=True)
        print(client_s)

        print("client request:")
        if use_stream:
            # both CPython and MicroPython SSLSocket objects support read() and
            # write() methods
            #
            # browsers are prone to terminate SSL connection abruptly if they
            # see unknown certificate, etc. We must continue in such case -
            # next request they issue will likely be more well-behaving and
            # will succeed
            try:
                req = client_s.readline().decode('utf-8').strip()
                print(INDENT + req)

                # content length
                length = 0

                # read headers, and look for Content-Length header
                while True:
                    h = client_s.readline()
                    if h == b"" or h == b"\r\n":
                        break
                    header = h.decode('utf-8').strip().lower()
                    if header.startswith('content-length'):
                        length = int(header.split(':')[1])
                    print(INDENT + header)

                # process data from the web form
                if req.startswith('POST') and length > 0:
                    data = client_s.read(length).decode('utf-8')
                    if data:
                        params = data.split('&')
                        ssid = None
                        password = None
                        key = None
                        for param in params:
                            if param.startswith('ssid='):
                                ssid = param.split('=')[1]
                            if param.startswith('pass='):
                                password = param.split('=')[1]
                            if param.startswith('key='):
                                key = param.split('=')[1]

                        if ssid and password:
                            write_settings_wifi(ssid, password)
                            client_s.write(SETTINGS_BYE)
                            client_s.close()
                            reboot()
                        if key:
                            write_settings_thingspeak(key)
                            client_s.write(SETTINGS_BYE)
                            client_s.close()
                            reboot()

                # print out html form
                if req:
                    client_s.write(SETTINGS_FORM)
            except Exception as e:
                print("exception: ", e)
        else:
            print(client_s.recv(4096))
            client_s.send(SETTINGS_FORM)

        # close the connection
        client_s.close()

# reboot the board after some delay
def reboot():
    import time
    import machine
    print('rebooting ...')
    time.sleep(REBOOT_DELAY)
    machine.reset()

def write_settings_wifi(ssid, password):
    f = open(SETTINGS_FILE_WIFI, 'w')
    f.write(ssid + '/' + password)
    f.close()

def write_settings_thingspeak(key):
    f = open(SETTINGS_FILE_THINGSPEAK, 'w')
    f.write(key)
    f.close()

# start wifi access point
def start_access_point():
    import network
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=CONFIG_WIFI_SSID, password=CONFIG_WIFI_PASSWORD, authmode=network.AUTH_WPA2_PSK)


config_mode = False

print('\nReading config file...')
read_err = read_config()
if read_err != 0:
    print('Forcing config mode.')
    config_mode = True

#TODO obczajanie przycisku po 2s od startu, jesli wcisniety
#start_access_point()
#start_local_server()
#reboot()

print('\n### Quitting boot.py ###')