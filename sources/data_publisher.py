# Publishing messages to TCP server

try:
    import usocket as socket
except:
    import socket

import message

class DataPublisher():
    def __init__(self, ip_address: str, port: int):
        self.ip_address = ip_address
        self.port = port
    
    def publish(self, messages: list):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.ip_address, self.port))
            data = message.create_packet(messages)
            sock.sendall(data)
            print('Data published.')
        except Exception as e: 
            print('Publish failed: ')
            print(e)
        finally:
            sock.close()