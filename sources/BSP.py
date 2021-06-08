# Board Support Package - low-level hardware handling

import machine, dht

# -------------------------------------------------------------------
# configuration and magic numbers
# -------------------------------------------------------------------

# number of samples to be taken into account when calculating moving-average of temperature and humidity
SENSOR_AVERAGE_SAMPLES = 10

# gpio definitions
RELAY_PIN = 5           # light relay
SENSOR_PIN = 4          # DHT sensor
PWM_PINS = [0,2,12,13]  # PWM for fans 1..4

# list of PWM objects to control fan outputs
fans = []

# Pin object to control relay
relay = None

#DHT21 sensor object, and moving-average of temperature (*C) and humidity (%)
sensor = None
temperature_average = 0
humidity_average = 0
sensor_first_measure = True



# -------------------------------------------------------------------
# main features
# -------------------------------------------------------------------

# initialize hardware
def init_all():
    global relay
    
    #init_fans()
    for i in range(4):
        fan_set(i, 0)

    init_sensor()

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
    if fans and fan < 4 and fans[fan]:
        fans[fan].duty((value * 1024) // 100)


# read the sensor to get data and update moving-average
# returns:  tuple of raw temperature and humidity in *C and %RH
def sensor_measure():
    global sensor, temperature_average, humidity_average, sensor_first_measure
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        
        if sensor_first_measure:
            sensor_first_measure = False
            temperature_average = temp
            humidity_average = hum
        else:
            temperature_average = ((temperature_average * (SENSOR_AVERAGE_SAMPLES-1)) + temp) / SENSOR_AVERAGE_SAMPLES
            humidity_average = ((humidity_average * (SENSOR_AVERAGE_SAMPLES-1)) + hum) / SENSOR_AVERAGE_SAMPLES
        return (temp, hum)
    except Exception as e:
        print('[ERR] Sensor measure failed:', e)
        return (0,0)


# get moving-average of temperature and humidity
# returns:  tuple of average temperature and humidity in *C and %RH
def sensor_get_average():
    return (temperature_average, humidity_average)



# -------------------------------------------------------------------
# aux functions
# -------------------------------------------------------------------

# initialize PWM outputs for fan control
def init_fans():
    global fans
    for pin in PWM_PINS:
        fans.append(machine.PWM(machine.Pin(pin), freq=100))


# initialize temperature and humidity sensor
def init_sensor():
    global sensor
    sensor = dht.DHT22(machine.Pin(SENSOR_PIN))
    
    #first readout fails, for some reason
    try:
        sensor.measure()
    except:
        pass