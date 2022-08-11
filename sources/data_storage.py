import os

# main log file name, do not change
STORAGE_FILE_NAME = 'storage.bin'

OS_FILE_STAT_SIZE_INDEX = 6

class DataStorage():
    # When isEspDevice=True, limited implementation is started, suitable for micropython (no dir path is used)
    def __init__(self, isEspDevice: bool = True, main_dir_path: str = None):
        if isEspDevice:
            self.main_dir_path = '.'
            self.storage_file_path = STORAGE_FILE_NAME
        else:
            from pathlib import Path
            self.main_dir_path = Path(main_dir_path)
            self.storage_file_path = self.main_dir_path / STORAGE_FILE_NAME
            self.main_dir_path.mkdir(parents=True, exist_ok=True)
        print("Storage file: %s" % (self.storage_file_path,))

        with open(self.storage_file_path, 'ab+'):
            pass

    # appends serialized data to storage file
    def append_data(self, serialized_data: bytes):
        with open(self.storage_file_path, 'ab+') as storage_file:
            storage_file.write(serialized_data)

    # clears the storage file and appends serialized data
    def clear_write_data(self, serialized_data: bytes):
        with open(self.storage_file_path, 'wb') as storage_file:
            storage_file.write(serialized_data)

    # clears all data from the storage file
    def clear_data(self):
        open(self.storage_file_path, 'w').close() # no "with" -> for ESP8266 compatibility

    # returns all data read from the storage file
    def read_all_data(self):
        with open(self.storage_file_path, 'rb') as storage_file:
            raw_data = storage_file.read()
        return raw_data

    # returns data read from the specific range of storage file
    def read_data(self, start_index, bytes_count):
        with open(self.storage_file_path, 'rb') as storage_file:
            storage_file.seek(start_index)
            raw_data = storage_file.read(bytes_count)
        return raw_data

    # returns size of the storage file in bytes
    def check_storage_size(self):
        return os.stat(self.storage_file_path)[OS_FILE_STAT_SIZE_INDEX]
