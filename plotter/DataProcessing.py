from scipy import interpolate
from scipy.signal import butter, filtfilt
from scipy.optimize import curve_fit
import numpy as np

def linearResampling(timeStamps:list, values:list, resampleTimeStep:float):
    """Resample non-uniform data using linear interpolation.
    resampleTimeStep - requested timesteps for output data"""
    timesResampled = np.arange(timeStamps[0], timeStamps[-1], resampleTimeStep)
    interpolation = interpolate.interp1d(timeStamps, values)
    valuesResampled = interpolation(timesResampled)
    return timesResampled, valuesResampled

def movingAverage(sampledInput:list, windowLength:int):
    average = float(sampledInput[0])
    outputList = []
    for sample in sampledInput:
        average = (average*(windowLength-1) + sample) / windowLength
        outputList.append(average)
    return outputList

def lowPassFilter(input:list, samplingPeriod:float, cutoffFrequency:float, order:int):
    """Apply low pass Butterworth filter.
    samplingPeriod: input signal sample period [s]
    cutoffFrequency: low pass cutoff frequency [Hz]
    order: order of the filter
    
    Based on:
    https://medium.com/analytics-vidhya/how-to-filter-noise-with-a-low-pass-filter-python-885223e5e9b7"""
    normalCutoff = 0.5 * cutoffFrequency * samplingPeriod
    b, a = butter(order, normalCutoff, analog=False)
    return filtfilt(b, a, input)

def approximateFunction(x:list, y:list, xNew:list, polynomialOrder:int = 2):
    """approximate curve using polynomial function of given order.
    
    returns a tuple of:
    - curve values for given xNew
    - calculated polynomial coefficients"""
    coeffs = np.polyfit(x, y, polynomialOrder)
    model = np.poly1d(coeffs)
    return model(xNew), coeffs

def solvePolynomialForY(coefficients, y):
    """source: https://stackoverflow.com/questions/16827053/solving-for-x-values-of-polynomial-with-known-y-in-scipy-numpy"""
    pc = coefficients.copy()
    pc[-1] -= y
    return np.roots(pc)