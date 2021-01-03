import network, utime
import usocket as socket

# run a local webserver
# host - IP address of the interface to run the server on
# port - server port
# maxclients - number of available connections in the same time
# process_callback(data) - function to be executed on GET request
#   data = dictionary containing data sent by the user
#   if it returns 255, server is stopped
# respond_callback(process_result) - function to generate server response
#TODO
#   process_result = value returned by process callback, might be used by user for generating different responses
def start(host, port=80, maxclients=2, process_callback=None, respond_callback=None):
    try:
        s = socket.socket()
        ai = socket.getaddrinfo(host, port)
        addr = ai[0][-1]
        s.bind(addr)
        s.listen(maxclients)
        print('Webserver started on %s:%d' % (host, port))

        running = True
        while running:
            try:
                conn, addr = s.accept()
                print('Connection from %s' % str(addr))
                request = conn.recv(1024)
                request = request.decode() #bytes to string
                if ('\r\n\r\n' in request):
                    print('===FULL===\n')
                else:
                    print('===NOT FULL===\n')

                #parsing user data
                data = {}
                try:
                    pos1 = request.find('GET /?')
                    if pos1 >= 0:
                        #request has GET data sent from the user - parse
                        pos2 = request.find(' HTTP')
                        request = request[pos1+6 : pos2]
                    
                        for field in request.split('&'):
                            k, v = field.split('=')
                            data[k] = v
                except Exception as e:
                    print(e)
                    
                #processing data
                result = 0
                if process_callback != None:
                    result = process_callback(data)

                #sending response
                if respond_callback != None:
                    respond_callback(conn, result)
                    #respond = respond_callback(result)
                    #conn.send(respond)

                conn.close()

                #stopping server
                if result == 255:
                    running = False
            except Exception as e:
                print(e)
        
        utime.sleep_ms(500)
        s.close()
        print('Webserver stopped.')

    except Exception as e: 
        print(e)
