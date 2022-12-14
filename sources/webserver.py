import network, utime, gc
import usocket as socket

# -------------------------------------------------------------------
# configuration
# -------------------------------------------------------------------

# maximum size in bytes for a single chunk of HTML file content
# NOTE: splitting is necessary to avoid memory allocation error when sending via TCP
BUFFER_MAX_SIZE = 500


# TCP socket opened by the user to send HTTP response to
TCP_SOCK = None

# webpage code splitted to chunks, including empty fields for user data when '%s' occured
WEBPAGE_SPLITTED = [] 

# indexes of empty fields in WEBPAGE_SPLITTED - instead of them, user data will be sent
WEBPAGE_INSERT_INDEX = []

# user data to be injected instead of '%s'
WEBPAGE_INSERT_DATA = []



# -------------------------------------------------------------------
# aux functions
# -------------------------------------------------------------------

# read HTML file and split it to chunks of maximum BUFFER_MAX_SIZE bytes
# also escape every occurance of '%s' for injecting user data
# filename - string, location of webpage to load
def load_webpage(filename):
    global WEBPAGE_SPLITTED
    global WEBPAGE_INSERT_INDEX
    global WEBPAGE_INSERT_DATA
    try:
        f = open(filename)
        buf = ''
        while True:
            buf = f.read(BUFFER_MAX_SIZE-1)
            if len(buf) == 0:
                #end of file
                break
            elif buf[-1] == '%':
                #possibly %s, read 1 more
                buf += f.read(1)
            
            #escape every %s
            pos = 0
            while buf:
                pos = buf.find('%s')
                if pos == 0:
                    #add escape item and save its index
                    WEBPAGE_SPLITTED.append('')
                    WEBPAGE_INSERT_INDEX.append(len(WEBPAGE_SPLITTED) - 1)
                    WEBPAGE_INSERT_DATA.append('')
                    buf = buf[2:]
                elif pos > 0:
                    #add regular item
                    WEBPAGE_SPLITTED.append(buf[:pos])
                    buf = buf[pos:]
                else:
                    #add rest of the buffer (no more %s)
                    WEBPAGE_SPLITTED.append(buf)
                    buf = ''
        print("Page loaded, escaped %i instances of '%%s'." % len(WEBPAGE_INSERT_DATA))
    finally:
        f.close()
    gc.collect()


# send response webpage stored in WEBPAGE_SPLITTED with injected user data stored in WEBPAGE_INSERT_DATA
# returns error code (0 = ok; 1 = no socket; 2 = unknown error)
def send_webpage():
    global TCP_SOCK
    if TCP_SOCK:
        try:
            data_index = 0
            for index in range(len(WEBPAGE_SPLITTED)):
                if index in WEBPAGE_INSERT_INDEX:
                    TCP_SOCK.write(WEBPAGE_INSERT_DATA[data_index])
                    data_index += 1
                else:
                    TCP_SOCK.write(WEBPAGE_SPLITTED[index])
            result = 0
        except:
            print('Error while sending HTTP response.')
            result = 2
    else:
        print('No socket specified.')
        result = 1

    gc.collect()
    return result


# run a local webserver
# host - IP address of the interface to run the server on
# port - server port
# index_filename - filename of the HTTP response file
# process_callback(data) - function to be executed on GET request
#     data = dictionary containing data sent by the user
#     if it returns 255, server is stopped
# respond_callback(process_result) - function to generate server response
#     process_result = value returned by process_callback, might be used by user for generating different responses
def start(host, port, index_filename, process_callback=None, respond_callback=None):
    global TCP_SOCK

    try:
        print('Loading webpage...')
        load_webpage(index_filename)
    except:
        print('Error while loading webpage from %.' % index_filename)

    try:
        s = socket.socket()
        ai = socket.getaddrinfo(host, port)
        addr = ai[0][-1]
        s.bind(addr)
        s.listen(1) #one connection at a time
        print('Webserver started on %s:%d' % (host, port))

        running = True
        while running:
            try:
                TCP_SOCK, addr = s.accept()
                request = ''
                while not '\r\n\r\n' in request: #double CRLF = end of HTTP request
                    request += TCP_SOCK.recv(1024).decode()

                print('\nConnection from %s' % str(addr))

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
                except:
                    print('Error while parsing user data.')
                    
                #processing data
                result = None
                if process_callback != None:
                    result = process_callback(data)

                #sending response
                if respond_callback != None:
                    respond_callback(result)

                #stopping server
                if result == 255:
                    running = False
            except Exception as e:
                print(e)
            finally:
                TCP_SOCK.close()
                utime.sleep_ms(500) #some time to avoid connection reset
                gc.collect()

    except Exception as e: 
        print(e)
    finally:
        s.close()
        print('Webserver stopped.')

    gc.collect()
