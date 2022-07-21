import socketserver, struct, time

from data_storage import DataStorage

STORAGE_DIR_PATH = 'storage/'

HOST, PORT = "0.0.0.0", 9999

# data packet: [time, temperature, humidity]
#   < - little endian
#   time - unsigned long long, seconds since unix epoch
#   temperature - float, celsius
#   humidity - float, percent
SERIALIZATION_FORMAT = '<Qff'

# data packet size in bytes
SERIALIZATION_SIZE = 16

storage = None

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        ip_address = self.client_address[0]
        payload = self.request.recv(1024) # TODO may not work for bigger chunks (cached), split and add timeout?
        message = deserialize(payload)        
        storage.append_data(payload)
        print(f"{format(message)}    [{ip_address}]")


def main():
    global storage

    print(f"Project X data storage server. Listening on {HOST}:{PORT}.\n")

    storage = DataStorage(STORAGE_DIR_PATH, deserialize)
    data = storage.read_data()
    print(f"Stored messages count: {len(data)}")
    if len(data) > 0:
        print(f"Last message:\n{format(data[-1])}\n")

    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()


def format(data: list):
    timestamp, temperature, humidity = data
    date_time = time.localtime(timestamp)
    date_time_str = time.strftime('%H:%M:%S %d.%m.%Y', date_time)
    return f"T = {temperature:.02f} *C     RH = {humidity:.02f} %    {date_time_str}"


# Serialize given data list
def serialize(data: list):
    return struct.pack(SERIALIZATION_FORMAT, *data)


# Deserialize packed data using given format
def deserialize(data_stream: bytes):
    try:
        packets = _split_data_into_packets(data_stream)
        result = [ \
            struct.unpack(SERIALIZATION_FORMAT, packet) \
            for packet in packets]
        if len(result) == 1:
            return result[0]
        return result
    except:
        return []


def _split_data_into_packets(data_stream: bytes):
    return [ \
        data_stream[SERIALIZATION_SIZE*i : SERIALIZATION_SIZE*(i+1)] \
        for i in range(0, len(data_stream)//SERIALIZATION_SIZE)]


if __name__ == "__main__":
    main()