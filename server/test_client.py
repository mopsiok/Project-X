import socket, sys, time

HOST, PORT = "0.0.0.0", 9999
data = " ".join(sys.argv[1:])

for i in range(3):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            payload = '[%02i] %s' % (i+1, data)
            sock.sendall(bytes(payload, "utf-8"))
        time.sleep(1)
    except Exception as e: 
        print('Publish failed: ')
        print(e)
