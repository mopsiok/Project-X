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


#####################################################################
#                       Main application
#####################################################################

storage = None

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        ip_address = self.client_address[0]
        payload = message.receive_packet(self.request.recv)
        messages = message.parse_messages(payload)

        # TODO add timeout?

        storage.append_data(payload)
        for i in range(len(messages)):
            print(f"{message.format(messages[i])}    [{ip_address}]  [{i+1:3d}]")


def main():
    global storage

    print(f"Project X data storage server. Listening on {SERVER_HOST}:{SERVER_PORT}.\n")

    storage = data_storage.DataStorage(STORAGE_DIRECTORY_PATH)
    data = storage.read_data()
    data = message.parse_messages(data)
    print(f"Stored messages count: {len(data)}")
    if len(data) > 0:
        print(f"Last message:\n{message.format(data[-1])}\n")

    with socketserver.TCPServer((SERVER_HOST, SERVER_PORT), MyTCPHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()