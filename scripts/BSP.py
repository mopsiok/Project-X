# Board Support Package - low-level hardware handling

import gc, machine
gc.collect()

# -------------------------------------------------------------------
# configuration and magic numbers
# -------------------------------------------------------------------

# gpio definitions
RELAY_PIN = 5           # light relay
SENSOR_PIN = 4          # DHT sensor
PWM_PINS = [0,2,14,15]  # PWM for fans 1..4
SCL_PIN = 12            # aux I2C clock
SDA_PIN = 13            # aux I2C data

# list of PWM objects to control fan outputs
fans = []

# Pin object to control relay
relay = None


#TODO reading temperature and humidity, function for getting moving average value of frequently read sensor


# -------------------------------------------------------------------
# main features
# -------------------------------------------------------------------

# initialize hardware
def init_all():
    global relay
    
    init_fans()
    for i in range(4):
        fan_set(i, 0)

    relay = machine.Pin(RELAY_PIN, machine.Pin.OUT)
    relay_off()


# deactivate relay's coil
def relay_off():
    global relay
    if relay:
        relay.off()


# activate relay's coil
def relay_on():
    global relay
    if relay:
        relay.on()


# set single fan output to required duty cycle
# fan:      0..3, index of fan
# value:    0..100, duty cycle in %
def fan_set(fan, value):
    global fans
    if fans and fan < 4:
        fans[fan].duty((value * 1024) // 100)



# -------------------------------------------------------------------
# aux functions
# -------------------------------------------------------------------

# initialize PWM outputs for fan control
def init_fans():
    global fans
    for pin in PWM_PINS:
        fans.append(machine.PWM(machine.Pin(pin), freq=100))