import socketserver

import message
from data_storage import DataStorage

STORAGE_DIR_PATH = 'storage/'

HOST, PORT = "0.0.0.0", 9999


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

    print(f"Project X data storage server. Listening on {HOST}:{PORT}.\n")

    storage = DataStorage(STORAGE_DIR_PATH, message.parse_messages)
    data = storage.read_data()
    print(f"Stored messages count: {len(data)}")
    if len(data) > 0:
        print(f"Last message:\n{message.format(data[-1])}\n")

    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()