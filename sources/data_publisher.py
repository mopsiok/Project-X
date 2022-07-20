# Publishing messages to TCP server

try:
    import usocket as socket
except:
    import socket

import struct

# data packet: [time, temperature, humidity]
#   < - little endian
#   time - unsigned long long, seconds since linux epoch
#   temperature - float, celsius
#   humidity - float, percent
SERIALIZATION_FORMAT = '<Qff'

class DataPublisher():
    def __init__(self, ip_address: str, port: int):
        self.ip_address = ip_address
        self.port = port
    
    def publish(self, payload: str):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.ip_address, self.port))
            sock.sendall(bytes(payload, "utf-8"))
            print('Data published.')
        except Exception as e: 
            print('Publish failed: ')
            print(e)
        finally:
            sock.close()

    # Serialize given data list
    def serialize(self, time: int, temperature: float, humidity: float):
        return struct.pack(SERIALIZATION_FORMAT, time, temperature, humidity)

    # Deserialize packed data using given format
    def deserialize(self, data_stream: bytes):
        return struct.unpack(SERIALIZATION_FORMAT, data_stream)
