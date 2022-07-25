# main log file name, do not change
STORAGE_FILE_NAME = 'storage.bin'

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
    
    # when path is None, default storage file is used
    # returns all data read from the file
    def read_data(self, storage_file_path: str = None):
        if not storage_file_path:
            storage_file_path = self.storage_file_path
        with open(storage_file_path, 'rb') as storage_file:
            raw_data = storage_file.read()
        return raw_data

    # when path is None, default storage file is used
    # clears all data from the file
    def clear_data(self, storage_file_path: str = None):
        if not storage_file_path:
            storage_file_path = self.storage_file_path
        open(storage_file_path, 'w').close()
