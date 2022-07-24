import socket, time
from pathlib import Path
import os, sys

#####################################################################
#                           Config
#####################################################################

# path to storage directory, where all data and backups stored
STORAGE_DIRECTORY_PATH = "storage/"

# TCP port to listen for new data
SERVER_PORT = 9999

REPEAT_COUNT = 30
CONNECTION_FAILED_REBOOT_COUNT = 10
SINGLE_PACKET_MESSAGE_COUNT = 1


#####################################################################
#                    Not config, don't change
#####################################################################

# path to ESP8266 side implementation - needed to import shared modules
ESP8266_SOURCES_PATH = "../sources"

SERVER_HOST = "localhost"


#####################################################################
#              Auxiliary functions and environment setup
#####################################################################

# Returns directory path of given file (this file used if no arguments)
def _get_directory_path(file : str = __file__):
    return Path(os.path.dirname(os.path.realpath(file)))

# Extend python path to enable importing shared modules
def shared_modules_init():
    dir_path = _get_directory_path()
    esp_modules_path = os.path.realpath(dir_path / ESP8266_SOURCES_PATH)
    sys.path.append(esp_modules_path)

shared_modules_init()
import message
import data_storage


#####################################################################
#                       Main application
#####################################################################

class DataPublisher():
    def __init__(self, ip_address: str, port: int):
        self.ip_address = ip_address
        self.port = port
    
    # returns True if publish successful, False otherwise
    def publish(self, messages: list):
        result = True
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.ip_address, self.port))
            data = message.create_packet(messages)
            sock.sendall(data)
            print('Data published.')
        except Exception as e: 
            print('Publish failed: ')
            print(e)
            result = False
        finally:
            sock.close()
        return result


def generate_messages(count: int = 1):
    message_list = []
    timestamp = int(time.time())
    for i in range(count):
        msg = [timestamp+i, 20+i, 50+i]
        message_list.append(msg)
    return message_list


# in case of transmission error, reconnect to WiFi (or reboot if it doesn't help)
def publish_fail_counter_handler():
    global fail_counter
    fail_counter += 1
    if fail_counter > CONNECTION_FAILED_REBOOT_COUNT:
        print('Maximum number of connection failures exceeded. The device will reboot.')
        exit()
    else:
        print('Connection failure (%03i), trying to reconnect to router. (Max failure time: %d sec)' % (fail_counter, CONNECTION_FAILED_REBOOT_COUNT))


# reset fail counter if the connection is restored
def publish_fail_counter_reset():
    global fail_counter
    fail_counter = 0


fail_counter = 0
publisher = DataPublisher(SERVER_HOST, SERVER_PORT)
messages = generate_messages(SINGLE_PACKET_MESSAGE_COUNT)

for i in range(REPEAT_COUNT):
    success = publisher.publish(messages)
    if not success:
        publish_fail_counter_handler()
    else:
        publish_fail_counter_reset()
    time.sleep(0.2)
