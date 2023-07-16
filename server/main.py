import socketserver
from common import *

#####################################################################
#                    Not config, don't change
#####################################################################

SERVER_HOST = "0.0.0.0"


#####################################################################
#                       Main application
#####################################################################

dataStorage = None
dataCache = None

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global dataCache

        ip_address = self.client_address[0]
        payload = message.receive_packet(self.request.recv)
        messages = message.parse_messages(payload)

        messages_checked = remove_duplicated_samples(messages, dataCache.cache)
        is_misplaced = is_packet_misplaced(messages_checked, dataCache.cache)
        dataCache.save_messages_to_ram(messages_checked)
        
        if is_misplaced:
            print("[WARN] Received misplaced packet, repairing...")
            dataCache.cache = repair_misplaced_samples(dataCache.cache)
            serialized = serialize_samples(dataCache.cache)
            dataStorage.clear_write_data(serialized)
        else:
            serialized = serialize_samples(messages_checked)
            dataStorage.append_data(serialized)

        for count, msg in enumerate(messages_checked):
            print(f"{message.format(msg)}    [{ip_address}]  [{count+1:2d}]")


def main():
    global dataStorage, dataCache

    print(f"Project X data storage server. Listening on {SERVER_HOST}:{SERVER_PORT}.\n")

    dataStorage, dataCache = data_init()
    print_storage_info(dataCache.cache, 1)

    with socketserver.TCPServer((SERVER_HOST, SERVER_PORT), MyTCPHandler) as server:
        server.serve_forever()

if __name__ == "__main__":
    main()