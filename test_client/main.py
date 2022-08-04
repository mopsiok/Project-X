# This is a simplified, PC version of the code executed on ESP8266
# Any dependencies on hardware has been removed or changed.
# 
# It is not pretty and might not be fully up to date, as it's a debugging tool for testing purposes only.
# The clue is to simulate device's behaviour without need for time-consuming 
# recompilation, reflashing and reconfiguring the device each time a change is made.
# No unit tests for this project, sorry.

#####################################################################
#              Auxiliary functions and environment setup
#####################################################################

from pathlib import Path
import os, sys, time

# path to ESP8266 side implementation - needed to import shared modules
ESP8266_SOURCES_PATH = "../sources"

# Returns directory path of given file (this file used if no arguments)
def _get_directory_path(file : str = __file__):
    return Path(os.path.dirname(os.path.realpath(file)))

# Extend python path to enable importing shared modules
def shared_modules_init():
    dir_path = _get_directory_path()
    esp_modules_path = os.path.realpath(dir_path / ESP8266_SOURCES_PATH)
    sys.path.append(esp_modules_path)

shared_modules_init()
import config, data_publisher, data_storage, data_cache, message
import timing_mock as timing
import bsp_mock as bsp

# -------------------------------------------------------------------
# configuration and magic numbers
# -------------------------------------------------------------------

# path to storage directory, where all data and backups stored
STORAGE_DIRECTORY_PATH = "storage/"

LOOP_DELAY_S = 0.001

# configuration dictionary
CONFIG = {} 


# periodic "tasks" refresh rates [in s]
HARDWARE_UPDATE_PERIOD = 1
SENSOR_READ_PERIOD = 5
#SERVER_PUBLISH_PERIOD is derived from CONFIG
NTP_SYNC_PERIOD = 60
GARBAGE_COLLECTOR_PERIOD = 10
FLASH_STORAGE_PERIOD = 60*15 # saving RAM cache into FLASH when server is unavailable

# NTP server trigger period [in s] in case when time hasn't been synchronized after reset
NTP_SYNC_PERIOD_AFTER_RESET = 5

# duration [in s] of constantly failing connections to the server, until the device reboots
CONNECTION_FAILED_REBOOT_TIME = 60*60*3


# -------------------------------------------------------------------
# aux functions
# -------------------------------------------------------------------

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

# in case of transmission error, reconnect to WiFi (or reboot if it doesn't help)
def publish_fail_counter_handler():
    global fail_counter, cache
    fail_counter += 1
    period = int(CONFIG['SERVER_PUBLISH_PERIOD'])
    if fail_counter * period > CONNECTION_FAILED_REBOOT_TIME:
        print('Maximum number of connection failures exceeded. The device will reboot.')
        cache.save_cache_to_flash()
        exit()
    else:
        print('Connection failed (%03i). Max failure time: %d sec' % (fail_counter, CONNECTION_FAILED_REBOOT_TIME))
        wifi_disconnect()
        wifi_connect(CONFIG.get('WIFI_SSID'), CONFIG.get('WIFI_PASS'), 5000)

# reset fail counter if the connection is restored
def publish_fail_counter_reset():
    global fail_counter
    fail_counter = 0



# -------------------------------------------------------------------
# wifi-related functions
# -------------------------------------------------------------------

# connect to a WiFi network
# ssid:     string
# password: string
# timeout:  int, maximum timeout in ms
# returns:  error code (0 = connected; 1 = missing credentials; 2 = timeout) and configuration info
def wifi_connect(ssid, password, timeout=10000):
    return 0, ('127.0.0.1',)


# disconnect from a WiFi network
def wifi_disconnect():
    pass


# -------------------------------------------------------------------
# main application timer, executed once in a second
# -------------------------------------------------------------------

TIMER_SERVER_PUBLISH = 0 #period for this timer is updated once CONFIG is read
TIMER_HARDWARE_UPDATE = 1
TIMER_SENSOR_READ = 2
TIMER_NTP_SYNC = 3
TIMER_GARBAGE_COLLECTOR = 4
TIMER_FLASH_STORAGE = 5
timer_periods = [0, HARDWARE_UPDATE_PERIOD, SENSOR_READ_PERIOD, NTP_SYNC_PERIOD, GARBAGE_COLLECTOR_PERIOD, FLASH_STORAGE_PERIOD]
timer_counters = [0,] * len(timer_periods)
timer_flags = [False,] * len(timer_periods)
def main_timer_callback(tim):
    global timer_periods, timer_counters, timer_flags
    for t in range(len(timer_periods)):
        timer_counters[t] += 1
        if timer_counters[t] >= timer_periods[t]:
            timer_counters[t] = 0
            timer_flags[t] = True


# schedule faster, manual re-connection to NTP server, when no sync is achieved after device reset
def manual_ntp_trigger():
    global timer_periods, timer_counters
    value = timer_periods[TIMER_NTP_SYNC] - NTP_SYNC_PERIOD_AFTER_RESET
    timer_counters[TIMER_NTP_SYNC] = value


# set relay and fans according to current time
# day_flag: True = day; False - night
def update_hardware(day_flag):
    pass


# -------------------------------------------------------------------
# main program
# -------------------------------------------------------------------  

print('\n\n### Entering Main Application ###')

#reading config
err = config_read()
timer_periods[TIMER_SERVER_PUBLISH] = int(CONFIG['SERVER_PUBLISH_PERIOD'])

#connecting to WiFi
err, network_info = wifi_connect(CONFIG.get('WIFI_SSID'), CONFIG.get('WIFI_PASS'))
ip = network_info[0]

server_ip = CONFIG.get('SERVER_IP')
server_port = int(CONFIG.get('SERVER_PORT'))
publisher = data_publisher.DataPublisher(server_ip, server_port)
storage = data_storage.DataStorage(False, STORAGE_DIRECTORY_PATH) #this is different in ESP implementation
cache = data_cache.DataCache(storage, publisher)

#getting time
err = timing.ntp_synchronize()
if err == 0:
    print("Synchronized to %i.%02i.%02i %02i:%02i:%02i" % timing.get_datetime())
else:
    print("Temporarily set set to %i.%02i.%02i %02i:%02i:%02i" % timing.get_datetime())
    manual_ntp_trigger()

#used to restart WiFi or reboot device if constantly failed to publish messages
fail_counter = 0

while True:
    try:
        main_timer_callback(None)

        #updating hardware
        if timer_flags[TIMER_HARDWARE_UPDATE]:
            timer_flags[TIMER_HARDWARE_UPDATE] = False
            try:
                day_flag = timing.check_day_mode(CONFIG['LIGHT_ON'], CONFIG['LIGHT_OFF'])
                update_hardware(day_flag)

                h,m,s = timing.get_time()
                print('%02i:%02i:%02i - %s' % (h, m, s, ('DAY TIME' if day_flag else 'NIGHT TIME')))
            except Exception as e:
                print('[ERR] Hardware update failed:',e)

        #reading the sensor
        if timer_flags[TIMER_SENSOR_READ]:
            timer_flags[TIMER_SENSOR_READ] = False
            temp, hum = bsp.sensor_measure()
            print('Sensor: %04.1f*C, %04.1f%%' % (temp, hum))
        
        #sending data to the server
        if timer_flags[TIMER_SERVER_PUBLISH]:
            timer_flags[TIMER_SERVER_PUBLISH] = False
            temp, hum = bsp.sensor_get_average()
            time_ = timing.get_timestamp()
            msg = [time_, temp, hum]
            
            cache.save_messages_to_ram([msg,])
            success = cache.publish_flash_messages_and_clear() #send flash messages first, as they were created earlier
            if success:
                success = cache.publish_ram_messages_and_clear()
            if success:
                publish_fail_counter_reset()
            else:
                publish_fail_counter_handler()

        # saving RAM cache into FLASH storage, when server is unavailable
        if timer_flags[TIMER_FLASH_STORAGE]:
            timer_flags[TIMER_FLASH_STORAGE] = False
            if fail_counter > 0:
                cache.save_cache_to_flash()

        #time synchronization
        if timer_flags[TIMER_NTP_SYNC]:
            timer_flags[TIMER_NTP_SYNC] = False
            if timing.ntp_synchronize() == 0:
                print('NTP synchronization completed.')
            else:
                # manual, faster trigger when there is still no synchronization after reboot
                if not timing.is_synchronized():
                    manual_ntp_trigger()

        #garbage collector
        if timer_flags[TIMER_GARBAGE_COLLECTOR]:
            pass

    except Exception as e:
        print('[ERR] Unhandled exception inside main loop:',e)

    time.sleep(LOOP_DELAY_S) #for background tasks to run

#unhandled error occured - rebooting
print('[ERR] Gone outside of main loop!')
safety.reboot()

print('\n\n### Quitting Main Application ###')