import socketserver, struct, time

# data packet: [time, temperature, humidity]
#   < - little endian
#   time - unsigned long long, seconds since unix epoch
#   temperature - float, celsius
#   humidity - float, percent
SERIALIZATION_FORMAT = '<Qff'

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        ip_address = self.client_address[0]
        payload = self.request.recv(1024)
        
        timestamp, temperature, humidity = deserialize(payload)
        date_time = time.localtime(timestamp)
        date_time_str = time.strftime('%H:%M:%S %d.%m.%Y', date_time)

        print(f"\n{ip_address} wrote:\n{payload}")
        print(f"   timestamp:    {timestamp}  ({date_time_str})")
        print(f"   temperature:  {temperature:.02f} *C")
        print(f"   humidity:     {humidity:.02f} %")

        


def main():
    HOST, PORT = "0.0.0.0", 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()

# Serialize given data list
def serialize(time: int, temperature: float, humidity: float):
    return struct.pack(SERIALIZATION_FORMAT, time, temperature, humidity)

# Deserialize packed data using given format
def deserialize(data_stream: bytes):
    return struct.unpack(SERIALIZATION_FORMAT, data_stream)

if __name__ == "__main__":
    main()