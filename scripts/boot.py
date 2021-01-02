# This file is executed on every boot (including wake-boot from deepsleep)

import esp, gc, sys, webrepl, network, machine, utime
from machine import Pin

import config, webserver

esp.osdebug(None) #turn off vendor O/S debugging messages
webrepl.start()
gc.collect()



# -------------------------------------------------------------------
# configuration
# -------------------------------------------------------------------

AP_SSID = 'PROJECT_X'
AP_PASSWORD = 'P4prykowe'

SERVER_INDEX = 'boot_index.html'

CONFIG = {}



# -------------------------------------------------------------------
# magic numbers
# -------------------------------------------------------------------

BOOT_BUTTON_PIN = 0 # boot button gpio (flash pin)
BOOT_ENTER_DELAY = 3000 # waiting period before checking button status (in ms)
BOOT_CLOSE_DELAY = 2000 # waiting period for finishing connection after AP stop request (in ms)

LED_PIN = 2 # status led gpio pin

# possible webserver responses
SERVER_PROCESS_EMPTY = 0
SERVER_PROCESS_SAVE = 1
SERVER_PROCESS_INCOMPLETE = 2
SERVER_PROCESS_ERROR = 254
SERVER_PROCESS_REBOOT = 255



# -------------------------------------------------------------------
# aux functions
# -------------------------------------------------------------------

# light on the status led
def led_on():
    global led
    led.off()


# light off the status led
def led_off():
    global led
    led.on()


# reboot the board
def esp_reboot():
    print('\nRebooting ...')
    machine.reset()


# start wifi access point and returns its network info (ip, mask, gateway, dns)
def access_point_start(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=password, authmode=network.AUTH_WPA2_PSK)
    utime.sleep_ms(500)
    info = ap.ifconfig()
    print('Access Point started (%s,%s)' % (ssid,password))
    print('Network info:', info)
    return info


# stop wifi access point
def access_point_stop():
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    print('Access Point stopped.')


# response webpage to be returned to the user
def server_respond(process_result=SERVER_PROCESS_EMPTY):
    info = ''
    if process_result == SERVER_PROCESS_SAVE:
        info = 'Configuration saved.'
    elif process_result == SERVER_PROCESS_INCOMPLETE:
        info = 'Incomplete data.'
    elif process_result == SERVER_PROCESS_ERROR:
        info = 'Unexpected error.'
    elif process_result == SERVER_PROCESS_REBOOT:
        info = 'Rebooting...'

    try:
        f = open(SERVER_INDEX)
        html = f.read()
        html = html % (CONFIG.get('WIFI_SSID'), CONFIG.get('WIFI_PASS'), info)
    finally:
        f.close()
    
    return html


# execute data received from user (if 255 returned, the sever will stop)
def server_process_data(data):
    try:
        ssid = data.get('WIFI_SSID')
        password = data.get('WIFI_PASS')
        reboot = data.get('REBOOT')

        print('GET data: ssid=%s password=%s reboot=%s' % (ssid, password, reboot))

        if (reboot == None) and (ssid == None) and (password == None):
            return SERVER_PROCESS_EMPTY

        if (reboot != None) and (reboot != ''):
            return SERVER_PROCESS_REBOOT
        else:
            if (ssid != None) and (ssid != '') and (password != None) and (password != ''):
                CONFIG['WIFI_SSID'] = ssid
                CONFIG['WIFI_PASS'] = password
                config.boot_write()
                return SERVER_PROCESS_SAVE
            else:
                return SERVER_PROCESS_INCOMPLETE
    except Exception as e:
        sys.print_exception(e)

    return SERVER_PROCESS_ERROR



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
            break

# entering config mode
if config_mode:
    print('\n[CONFIG MODE]')
    led_on()

    network_info = access_point_start(AP_SSID, AP_PASSWORD)
    ip = network_info[0]

    webserver.start(ip, process_callback=server_process_data, respond_callback=server_respond)

    print('Stopping Access Point...')
    utime.sleep_ms(BOOT_CLOSE_DELAY)
    access_point_stop()
    utime.sleep_ms(100)
    esp_reboot()
else:
    print('\n[NORMAL MODE]')

led_off()

print('\n### Quitting boot.py ###')