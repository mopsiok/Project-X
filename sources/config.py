# Reading and writing configuration

# -------------------------------------------------------------------
# configuration
# -------------------------------------------------------------------

CONFIG_FILE = 'boot.conf'
SETTINGS_DELIM = ' := '




# -------------------------------------------------------------------
# main functions
# -------------------------------------------------------------------

# read configuration from file to dictionary and return error code
# config:       dict, output config object
# returns:      0 = OK; 1 = read error
def read(config):
    result = 0
    try:
        f = open(CONFIG_FILE, 'r')
        config.clear()
        while True:
            line = f.readline()
            if len(line) > 0:
                line = line.replace('\r', '').replace('\n', '')
                try:
                    key,value = line.split(SETTINGS_DELIM)
                    config[key] = value
                except:
                    pass
            else:
                break
    except Exception as e:
        print(e)
        result = 1
    finally:
        f.close()
    return result


# write config dictionary to file and return error code
# config:       dict, input config object
# returns:      0 = OK; 1 = write error
def write(config):
    result = 0
    try:
        f = open(CONFIG_FILE, 'w')
        for key in config:
            f.write(key + SETTINGS_DELIM + config.get(key) + '\n')
    except Exception as e:
        print(e)
        result = 1
    finally:
        f.close()
    return result