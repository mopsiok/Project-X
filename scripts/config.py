# Reading and writing configuration

# -------------------------------------------------------------------
# configuration
# -------------------------------------------------------------------

SETTINGS_DELIM = ' := '

BOOT_FILE = 'boot.conf'
BOOT_REQUIRED_KEYS = ('WIFI_SSID','WIFI_PASS')
BOOT_CONFIG = {}

MAIN_FILE = 'main.conf'
MAIN_REQUIRED_KEYS = ('MQTT_SERVER','MQTT_CHANNEL_ID','MQTT_WRITE_KEY','MQTT_PUBLISH_PERIOD')
MAIN_CONFIG = {}



# -------------------------------------------------------------------
# low-level read/write functions
# -------------------------------------------------------------------

# read configuration from file, check if it is complete and return error code and config dictionary
# error_code: 0 = OK; 1 = config not complete; 2 = read error
def read(filename, required_keys=[]):
    config_tmp = {}
    try:
        f = open(filename, 'r')
        tmp = f.read()
        tmp = tmp.replace('\r', '') #windows-style new line correction
        f.close()
        for line in tmp.split('\n'):
            try:
                key,value = line.split(SETTINGS_DELIM)
                config_tmp[key] = value
            except:
                pass
        
        print('Config file contents:')
        print(config_tmp)

        #check if every key is defined            
        if all (key in config_tmp.keys() for key in required_keys):
            print('Config OK')
            return (0, config_tmp)
        else:
            print('Config not complete')
            return (1, config_tmp)
    except Exception as e:
        print(e)
        return (2, config_tmp)


# write config dictionary to file and return error code
# error_code: 0 = OK; 1 = write error
def write(filename, config):
    try:
        tmp = ""
        for key in config:
            tmp += key + SETTINGS_DELIM + config.get(key) + '\n'

        f = open(filename, 'w')
        f.write(tmp)
        f.close()
        return 0
    except Exception as e:
        print(e)
        return 1



# -------------------------------------------------------------------
# high-level functions
# -------------------------------------------------------------------

# reads boot config file to global BOOT_CONFIG and returns error code
def boot_read():
    global BOOT_CONFIG
    
    print('\nReading boot config file...')
    err, config = read(BOOT_FILE, BOOT_REQUIRED_KEYS)
    for key in config:
        BOOT_CONFIG[key] = config.get(key)
    return err

# writes global BOOT_CONFIG to boot config file and returns error code
def boot_write():
    print('\nWriting boot config file...')
    err = write(BOOT_FILE, BOOT_CONFIG)
    return err

# reads main config file to global MAIN_CONFIG and returns error code
def main_read():
    global MAIN_CONFIG
    print('\nReading main config file...')
    err, config = read(MAIN_FILE, MAIN_REQUIRED_KEYS)
    for key in config:
        MAIN_CONFIG[key] = config.get(key)
    return err

# writes global MAIN_CONFIG to main config file and returns error code
def main_write():
    print('\nWriting main config file...')
    err = write(MAIN_FILE, MAIN_CONFIG)
    return err