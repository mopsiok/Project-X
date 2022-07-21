from pathlib import Path
import time

STORAGE_FILE_NAME = 'storage.bin'

class DataStorage():
    def __init__(self, main_dir_path, deserializer):
        self.main_dir_path = Path(main_dir_path)
        self.storage_file_path = self.main_dir_path / STORAGE_FILE_NAME
        self.deserializer = deserializer

        self.main_dir_path.mkdir(parents=True, exist_ok=True)
        with open(self.storage_file_path, 'ab+'):
            pass

    # appends serialized data to storage file
    # returns execution time (in seconds)
    def append_data(self, serialized_data: bytes):
        start = time.time()
        with open(self.storage_file_path, 'ab') as storage_file:
            storage_file.write(serialized_data)
        return time.time() - start
    
    # when path is None, default storage file is used
    # returns list of messages, each deserialized to data list
    def read_data(self, storage_file_path = None):
        if not storage_file_path:
            storage_file_path = self.storage_file_path
        with open(storage_file_path, 'rb') as storage_file:
            raw_data = storage_file.read()
        return self.deserializer(raw_data)



