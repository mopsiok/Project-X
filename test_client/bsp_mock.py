# Board Support Package - low-level hardware handling

import random

# number of samples to be taken into account when calculating moving-average of temperature and humidity
SENSOR_AVERAGE_SAMPLES = 10

#DHT21 sensor object, and moving-average of temperature (*C) and humidity (%)
sensor = None
temperature_average = 0
humidity_average = 0
sensor_first_measure = True


# read the sensor to get data and update moving-average
# returns:  tuple of raw temperature and humidity in *C and %RH
def sensor_measure():
    global sensor, temperature_average, humidity_average, sensor_first_measure
    try:
        temp = random.randint(20, 30)
        hum = random.randint(40, 70)
        
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
