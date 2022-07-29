# Temporary cache manager for unsent data when TCP server is down.

import message
from data_storage import DataStorage
from data_publisher import DataPublisher, MESSAGES_PER_CHUNK

class DataCache():
    def __init__(self, storage: DataStorage, publisher: DataPublisher):
        self.cache = []
        self.storage = storage
        self.publisher = publisher
    
    # Saves given list of unsent messages into RAM cache
    def save_messages_to_ram(self, message_list: list):
        self.cache.extend(message_list)

    # Publish messages from RAM cache, clear it when successful
    # Returns True when publish OK
    def publish_ram_messages_and_clear(self):
        success = self.publisher.publish(self.cache)
        if success:
            self.cache = []
        return success

    # Publish messages from internal FLASH storage by chunks, clear the file when successful
    # Returns True when publish OK, False otherwise
    # Note: If publishing any chunk fails, the whole process stops and it needs to be restarted.
    # This is okey though, as server side checks for duplicated data and rejects it
    def publish_flash_messages_and_clear(self):
        size = self.storage.check_storage_size()
        if (size > 0):
            print('Trying to send %d messages from FLASH storage.' % (size,))

            # slicing into smaller chunks is needed as the file content might not fit in limited RAM of ESP8266
            offset = 0
            chunk_size = message.MESSAGE_SIZE * MESSAGES_PER_CHUNK
            while offset < size:
                raw_chunk = self.storage.read_data(offset, chunk_size)
                flash_data_chunk = message.parse_messages(raw_chunk)
                success = self.publisher.publish(flash_data_chunk)
                if not success:
                    return False
                offset += chunk_size
            print("FLASH data sent successfully, clearing internal storage.")
            self.storage.clear_data()
        return True

    # Main cache handler, execute periodically
    def handler(self):
        pass

