# Temporary cache for unsent data when TCP server is down.

import message
from data_storage import DataStorage
from data_publisher import DataPublisher

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
    def publish_ram_messages(self):
        success = self.publisher.publish(self.cache)
        if success:
            self.cache = []
        return success

    # Publish messages from internal FLASH storage, clear the file when successful
    # Returns True when publish OK
    def publish_flash_messages(self):
        flash_data = message.parse_messages(self.storage.read_data())
        success = self.publisher.publish(flash_data)
        if success:
            print("FLASH data sent successfully, clearing internal storage.")
            self.storage.clear_data()
        else:
            print("FLASH data publish failed.")
        return success

    # Main cache handler, execute periodically
    def handler(self):
        pass