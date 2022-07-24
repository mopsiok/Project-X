import struct, time

# header at the beginning of each tcp packet
#   < - little endian
#   length - unsigned long, number of bytes to read till the end of the packet
#   crc - unsigned long, checksum for length field
HEADER_FORMAT = '<LL'
HEADER_SIZE = 4 + 4

# data message: [time, temperature, humidity]
#   < - little endian
#   time - unsigned long, seconds since unix epoch
#   temperature - float, celsius
#   humidity - float, percent
MESSAGE_FORMAT = '<Lff'
MESSAGE_SIZE = 4 + 4 + 4

# Convert single message to its string representation
def format(message: list):
    timestamp, temperature, humidity = message
    date_time = time.localtime(timestamp)
    date_time_str = time.strftime('%H:%M:%S %d.%m.%Y', date_time)
    return "T = %.02f *C     RH = %.02f %%    %s" % (temperature, humidity, date_time_str)

# Serialize arbitrary data using given format
def serialize(data: list, format=MESSAGE_FORMAT):
    return struct.pack(format, *data)

# Deserialize packed data using given format
def deserialize(data_stream: bytes, format=MESSAGE_FORMAT):
    return struct.unpack(format, data_stream)

# Create single packet containing one or multiple messages
# returns serialized bytes
def create_packet(messages: list):
    payload_ser = b''.join(
        serialize(message, MESSAGE_FORMAT) for message in messages)

    length = len(payload_ser)
    crc = length # simplified check is used, implement proper one if needed
    header = [length, crc]
    header_ser = serialize(header, HEADER_FORMAT)
    return header_ser + payload_ser

# Receive single packet
# returns serialized payload containing messages
def receive_packet(receive_func):
    header_ser = receive_func(HEADER_SIZE)
    header = deserialize(header_ser, HEADER_FORMAT)
    length, crc = header

    # for now, CRC is a duplicated value of length field - implement properly if needed
    if length != crc:
        raise Exception("CRC check failed")
        
    return receive_func(length)

# Split given payload containing messages into single pieces,
# then deserialize each one and return as a list of messages
def parse_messages(payload: bytes):
    serialized = _split_payload_into_messages(payload)
    return [deserialize(message, MESSAGE_FORMAT) \
        for message in serialized]

def _split_payload_into_messages(data_stream: bytes):
    return [ \
        data_stream[MESSAGE_SIZE*i : MESSAGE_SIZE*(i+1)] \
        for i in range(0, len(data_stream)//MESSAGE_SIZE)]