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

# index of the timestamp value in single measurement tuple
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
#                       Data manipulation
#####################################################################

# returns sample's timestamp value
def get_sample_time(sample: list):
    return sample[TIMESTAMP_INDEX]

# checks whether received packet is misplaced based on current cache
def is_packet_misplaced(received_messages: list, cache: list):
    if (len(cache) == 0) or (len(received_messages) == 0):
        return False

    current_timestamp = get_sample_time(received_messages[0])
    last_timestamp = get_sample_time(cache[-1])
    return current_timestamp < last_timestamp

# in case of receiving packets in wrong order, sort the whole cache and return the result
def repair_misplaced_samples(cache: list):
    fixed = sorted(cache, key=lambda sample: sample[TIMESTAMP_INDEX])
    return fixed

# duplicated data rejection based on ram cache
def remove_duplicated_samples(received_messages: list, cache: list):
    checked_messages = []
    for msg in received_messages:
        if not msg in cache:
            checked_messages.append(msg)
    return checked_messages

# serialize given sample list
def serialize_samples(messages_list: list):
    return b''.join(message.serialize(msg) for msg in messages_list)

# info about sample list
def print_storage_info(messages_list: list, print_first: int=0):
    print(f"Stored messages count: {len(messages_list)}")
    length = len(messages_list)
    if length > 0:
        first_counter = 0
        while (first_counter < length) and (first_counter < print_first):
            print(f"Message {first_counter+1:05}: {message.format(messages_list[first_counter])}")
            first_counter += 1
        print(f"Message {length:05}: {message.format(messages_list[-1])}")


#####################################################################
#                       High-level data functions
#####################################################################

# initialize needed data objects
def data_init():
    dataStorage = data_storage.DataStorage(False, STORAGE_DIRECTORY_PATH)
    dataCache = data_cache.DataCache(dataStorage, None)
    data = dataStorage.read_all_data()
    data = message.parse_messages(data)
    dataCache.save_messages_to_ram(data)
    del data
    
    return dataStorage, dataCache
