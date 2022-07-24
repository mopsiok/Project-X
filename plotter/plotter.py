from generic_plot import GenericPlot
from data_storage import DataStorage
import message

from enum import Enum
from pathlib import Path
import os

#####################################################################
#                           Config
#####################################################################

# path to storage directory, where all ProjectX data and backups are stored
# pointing from this file's directory
STORAGE_DIRECTORY_PATH = "../server/storage"


#####################################################################
#                           Not config
#####################################################################

SECONDS_IN_DAY = 60*60*24


#####################################################################
#                   Project X plotting class
#####################################################################

class Plotter():
    def __init__(self,  start_date: int = None, 
                        end_date: int = None, 
                        duration: float = 1.0):
        try:
            period = round(duration * SECONDS_IN_DAY)
            if start_date == None:
                start_date = end_date - period
            if end_date == None:
                end_date = start_date + period
        except:
            raise Exception(PlotterExceptions.WRONG_ARGS)

        if end_date < start_date:
            start_date, end_date = end_date, start_date
        
        self.period = end_date - start_date
        self.start_date = start_date
        self.end_date = end_date

        print(f"start: {self.start_date}\nend: {self.end_date}\nperiod: {self.period/SECONDS_IN_DAY}")

        dir_path = _get_directory_path() / STORAGE_DIRECTORY_PATH
        storage = DataStorage(dir_path)
        data = storage.read_data()
        data = message.parse_messages(data)
        self.messages_list = data
        print(f"Storage read successful. Stored messages count: {len(data)}")
        if len(data) > 0:
            print(f"Last message: {message.format(data[-1])}\n")


    def plot_data(self):
        plot = GenericPlot()
        time_list, temp_list, hum_list = self._reshape_data(self.messages_list)

        print("timestamp:")
        print(" ".join(["%d" % item for item in time_list]))
        print("\n\ntemperature:")
        print(" ".join(["%.1f" % item for item in temp_list]))
        print("\n\nhumidity:")
        print(" ".join(["%.1f" % item for item in hum_list]))


    # Convert list of messages into separate arrays (axes)
    # Returns a tuple of type: 
    #   (timestamps: list[int], 
    #    temperatures: list[float], 
    #    humidity: list[float])
    def _reshape_data(self, messages: list):
        timestamps, temperatures, humidities = [], [], []
        for msg in messages:
            t, temp, hum = msg
            timestamps.append(t)
            temperatures.append(temp)
            humidities.append(hum)
        return timestamps, temperatures, humidities


class PlotterExceptions(Enum):
    WRONG_ARGS = "Wrong arguments"


#####################################################################
#                       Auxiliary functions
#####################################################################

# returns directory path of given file (this file used if no arguments)
def _get_directory_path(file : str = __file__):
    return Path(os.path.dirname(os.path.realpath(file)))