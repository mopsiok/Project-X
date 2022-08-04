import socketserver
from pathlib import Path
import os, sys

#####################################################################
#                           Config
#####################################################################

# path to storage directory, where all data and backups stored
STORAGE_DIRECTORY_PATH = "storage/"

# TCP port to listen for new data
SERVER_PORT = 9999


#####################################################################
#                    Not config, don't change
#####################################################################

# path to ESP8266 side implementation - needed to import shared modules
ESP8266_SOURCES_PATH = "../sources"

SERVER_HOST = "0.0.0.0"


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
import data_cache


#####################################################################
#                       Main application
#####################################################################

storage = None
cache = None

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        ip_address = self.client_address[0]
        payload = message.receive_packet(self.request.recv)
        messages = message.parse_messages(payload)

        # duplicated data rejection based on ram cache
        messages_checked = []
        for msg in messages:
            if not msg in cache.cache:
                messages_checked.append(msg)
        payload_checked = b''.join(
            message.serialize(msg) for msg in messages_checked)
        
        # updating cache and storage
        cache.save_messages_to_ram(messages_checked)
        storage.append_data(payload_checked)

        for count, msg in enumerate(messages_checked):
            print(f"{message.format(msg)}    [{ip_address}]  [{count+1:2d}]")


def main():
    global storage, cache

    print(f"Project X data storage server. Listening on {SERVER_HOST}:{SERVER_PORT}.\n")

    storage = data_storage.DataStorage(False, STORAGE_DIRECTORY_PATH)
    cache = data_cache.DataCache(storage, None)
    data = storage.read_all_data()
    data = message.parse_messages(data)
    cache.save_messages_to_ram(data)
    print(f"Stored messages count: {len(data)}")
    if len(data) > 0:
        print(f"Last message:\n{message.format(data[-1])}\n")
    del data

    with socketserver.TCPServer((SERVER_HOST, SERVER_PORT), MyTCPHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()