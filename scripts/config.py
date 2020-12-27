# Reading and writing configuration

# global config dictionary
CONFIG = {} 
SETTINGS_FILE = 'settings.conf'
SETTINGS_DELIM = ' := '
REQUIRED_KEYS = ('WIFI_SSID','WIFI_PASS',
                'MQTT_SERVER','MQTT_CHANNEL_ID','MQTT_WRITE_KEY','MQTT_PUBLISH_PERIOD')


# -------------------------------------------------------------------
# getting configuration from file
# -------------------------------------------------------------------

def read_config():
    global CONFIG
    config_tmp = {}
    try:
        f = open(SETTINGS_FILE, 'r')
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

        for key in config_tmp:
            CONFIG[key] = config_tmp[key]

        #check if every key is defined            
        if all (key in CONFIG.keys() for key in REQUIRED_KEYS):
            print('Config OK')
            return 0
        else:
            print('Config not complete')
            return 1
    except:
        print('Config read error')
        return 2


def write_config():
    try:
        tmp = ""
        for key in CONFIG:
            tmp += key + SETTINGS_DELIM + CONFIG.get(key) + '\n'

        f = open(SETTINGS_FILE, 'w')
        f.write(tmp)
        f.close()
        return 0

    except:
        print('Config write error')
        return 1