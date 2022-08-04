# Publishing messages to TCP server

try:
    import usocket as socket
except:
    import socket

import message

# DON'T CHANGE; max size of single TCP packet (in bytes) - needed because of ESP8266 limitation
MAX_TCP_PACKET_SIZE = 512

MESSAGES_PER_CHUNK = MAX_TCP_PACKET_SIZE // message.MESSAGE_SIZE

class DataPublisher():
    def __init__(self, ip_address: str, port: int):
        self.ip_address = ip_address
        self.port = port

    # Send given list of messages (sliced into separate chunks) to TCP server
    # Returns True when all data is sent properly
    def publish(self, messages: list):
        msg_count = len(messages)
        offset = 0
        while (offset < msg_count):
            chunk = messages[offset : offset + MESSAGES_PER_CHUNK]
            offset += MESSAGES_PER_CHUNK
            result = self._publish_single_chunk(chunk)
            if not result:
                return False
        return True

    
    # Open TCP connection and send given list of messages
    # returns True if publish successful, False otherwise
    def _publish_single_chunk(self, messages: list):
        if len(messages) > MESSAGES_PER_CHUNK:
            print('Message count exceeds %d, aborting.' % MESSAGES_PER_CHUNK)
            return False

        result = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.ip_address, self.port))
            data = message.create_packet(messages)
            sock.sendall(data)
            result = True
            print('Data published (msg count: %d).' % len(messages))
        except Exception as e: 
            print('Publish failed: ')
            print(e)
        finally:
            sock.close()
        return result