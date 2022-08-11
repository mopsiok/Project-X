import socketserver
from pathlib import Path
import os, sys

#####################################################################
#                           Config
#####################################################################

# path to storage directory, where all data and backups stored
STORAGE_DIRECTORY_PATH = "../binaries/"

# TCP port to listen for new data
SERVER_PORT = 9999


#####################################################################
#                    Not config, don't change
#####################################################################

# path to ESP8266 side implementation - needed to import shared modules
ESP8266_SOURCES_PATH = "../sources"

SERVER_HOST = "0.0.0.0"

TIMESTAMP_INDEX = 0


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

def get_sample_time(sample: list):
    return sample[TIMESTAMP_INDEX]

def is_packet_misplaced(received_messages: list):
    if (len(cache.cache) == 0) or (len(received_messages) == 0):
        return False

    current_timestamp = get_sample_time(received_messages[0])
    last_timestamp = get_sample_time(cache.cache[-1])
    return current_timestamp < last_timestamp

# in case of receiving packets in wrong order, sort the whole cache and return the result
def repair_misplaced_samples():
    fixed = sorted(cache.cache, key=lambda sample: sample[TIMESTAMP_INDEX])
    return fixed

# duplicated data rejection based on ram cache
def remove_duplicated_samples(received_messages: list):
    checked_messages = []
    for msg in received_messages:
        if not msg in cache.cache:
            checked_messages.append(msg)
    return checked_messages

def serialize_samples(messages_list: list):
    return b''.join(message.serialize(msg) for msg in messages_list)


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global cache

        ip_address = self.client_address[0]
        payload = message.receive_packet(self.request.recv)
        messages = message.parse_messages(payload)

        messages_checked = remove_duplicated_samples(messages)
        is_misplaced = is_packet_misplaced(messages_checked)
        cache.save_messages_to_ram(messages_checked)
        
        if is_misplaced:
            print("[WARN] Received misplaced packet, repairing...")
            messages_fixed = repair_misplaced_samples()
            cache.cache = messages_fixed
            serialized = serialize_samples(messages_fixed)
            storage.clear_write_data(serialized)
        else:
            serialized = serialize_samples(messages_checked)
            storage.append_data(serialized)

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