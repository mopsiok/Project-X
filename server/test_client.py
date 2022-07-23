import socket, time
import message

HOST, PORT = "0.0.0.0", 9999

message_list = []

def publish(messages: list):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
        data = message.create_packet(messages)
        sock.sendall(data)
        print('Data published.')
    except Exception as e: 
        print('Publish failed: ')
        print(e)
    finally:
        sock.close()

for i in range(4):
    msg = [int(time.time()), 20+i, 50+i]
    message_list.append(msg)
    publish(message_list)
    time.sleep(1)
