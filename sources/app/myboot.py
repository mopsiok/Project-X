# This file is executed on every boot (including wake-boot from deepsleep)

import esp, gc, webrepl, network, machine, utime
from machine import Pin

import app.config as config
import app.webserver as webserver
gc.collect()



# -------------------------------------------------------------------
# configuration
# -------------------------------------------------------------------

WEBREPL_PORT = 8266
WEBREPL_PASSWORD = 'papryk'

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
    print('Rebooting...')
    machine.reset()


# reads config file to global CONFIG and returns error code
def config_read():
    print('Reading config file.')
    err = config.read(CONFIG)
    print(CONFIG)
    return err


# writes global CONFIG to config file and returns error code
def config_write():
    print('Writing config file.')
    err = config.write(CONFIG)
    return err



# -------------------------------------------------------------------
# wifi functions
# -------------------------------------------------------------------

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



# -------------------------------------------------------------------
# webserver functions
# -------------------------------------------------------------------

# fill the response data list with user data
# info:     string, response message for the user
def server_update_response_data(info):
    webserver.WEBPAGE_INSERT_DATA[0] = CONFIG.get('WIFI_SSID')
    webserver.WEBPAGE_INSERT_DATA[1] = CONFIG.get('WIFI_PASS')
    webserver.WEBPAGE_INSERT_DATA[2] = CONFIG.get('LIGHT_ON')
    webserver.WEBPAGE_INSERT_DATA[3] = CONFIG.get('LIGHT_OFF')
    webserver.WEBPAGE_INSERT_DATA[4] = CONFIG.get('PWM1_DAY')
    webserver.WEBPAGE_INSERT_DATA[5] = CONFIG.get('PWM1_NIGHT')
    webserver.WEBPAGE_INSERT_DATA[6] = CONFIG.get('PWM2_DAY')
    webserver.WEBPAGE_INSERT_DATA[7] = CONFIG.get('PWM2_NIGHT')
    webserver.WEBPAGE_INSERT_DATA[8] = CONFIG.get('PWM3_DAY')
    webserver.WEBPAGE_INSERT_DATA[9] = CONFIG.get('PWM3_NIGHT')
    webserver.WEBPAGE_INSERT_DATA[10] = CONFIG.get('PWM4_DAY')
    webserver.WEBPAGE_INSERT_DATA[11] = CONFIG.get('PWM4_NIGHT')
    webserver.WEBPAGE_INSERT_DATA[12] = CONFIG.get('MQTT_SERVER')
    webserver.WEBPAGE_INSERT_DATA[13] = CONFIG.get('MQTT_CHANNEL_ID')
    webserver.WEBPAGE_INSERT_DATA[14] = CONFIG.get('MQTT_WRITE_KEY')
    webserver.WEBPAGE_INSERT_DATA[15] = CONFIG.get('MQTT_PUBLISH_PERIOD')
    webserver.WEBPAGE_INSERT_DATA[16] = info


# execute data received from user (if 255 returned, the server will stop)
# data:     string, data received via GET
def server_process_data(data):
    global CONFIG
    try:
        print("Received data:")
        print(data)

        if len(data) == 0:
            return SERVER_PROCESS_EMPTY

        if data.get('REBOOT'):
            return SERVER_PROCESS_REBOOT
        else:
            for key in data.keys():
                value = data[key]
                if (key in CONFIG.keys()) and value:
                    CONFIG[key] = value.replace('%3A', ':')

            config_write()
            return SERVER_PROCESS_SAVE
    except:
        print('Error while processing user data.')
        return SERVER_PROCESS_ERROR


# response webpage to be returned to the user
# process_result:   return code of process callback executing user data
def server_respond(process_result):
    info = ''
    if process_result == SERVER_PROCESS_SAVE:
        info = 'Configuration saved.'
    elif process_result == SERVER_PROCESS_ERROR:
        info = 'Unexpected error.'
    elif process_result == SERVER_PROCESS_REBOOT:
        info = 'Rebooting...'

    server_update_response_data(info)
    webserver.send_webpage()



# -------------------------------------------------------------------
# main program
# -------------------------------------------------------------------  

print('\n\n### Entering Bootloader ###')

#GPIO initialization
led = Pin(LED_PIN, Pin.OUT)
button = Pin(BOOT_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
led_off()

#starting webREPL service
webrepl.start(WEBREPL_PORT,WEBREPL_PASSWORD)

#reading config
err = config_read()
config_mode = False
if err != 0:
    print('Forcing config mode.')
    config_mode = True

#checking FLASH button for specifying configuration mode
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

if config_mode:
    #entering config mode
    print('[CONFIG MODE]')
    led_on()

    #connecting do WiFi
    network_info = access_point_start(AP_SSID, AP_PASSWORD)
    ip = network_info[0]

    #starting config webserver
    webserver.start(ip, 80, SERVER_INDEX, server_process_data, server_respond)

    #server is stopped on user demand or due to error - disabling AP and rebooting
    print('Stopping Access Point...')
    utime.sleep_ms(BOOT_CLOSE_DELAY)
    access_point_stop()
    utime.sleep_ms(100)
    esp_reboot()
else:
    print('[NORMAL MODE]')

led_off()

print('\n\n### Quitting Bootloader ###')