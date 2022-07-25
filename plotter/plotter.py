from enum import Enum
from pathlib import Path
import os, sys, time

#####################################################################
#                           Config
#####################################################################

# path to storage directory, where all ProjectX data and backups are stored
STORAGE_DIRECTORY_PATH = "../server/storage"


#####################################################################
#                    Not config, don't change
#####################################################################

# path to ESP8266 side implementation - needed to import shared modules
ESP8266_SOURCES_PATH = "../sources"

# path to Measurement Manager application directory - used to plot data
GENERIC_PLOTTER_SOURCES = "../external/measurement_manager/app"

SECONDS_IN_DAY = 60*60*24


#####################################################################
#              Auxiliary functions and environment setup
#####################################################################

# Returns directory path of given file (this file used if no arguments)
def _get_directory_path(file : str = __file__):
    return Path(os.path.dirname(os.path.realpath(file)))

# Extend python path to enable importing shared modules
def shared_modules_init():
    dir_path = _get_directory_path()
    esp_modules_path = os.path.realpath(dir_path / ESP8266_SOURCES_PATH)
    plotter_path = os.path.realpath(dir_path / GENERIC_PLOTTER_SOURCES)
    sys.path.append(esp_modules_path)
    sys.path.append(plotter_path)

shared_modules_init()
import message
from data_storage import DataStorage

# Measurement Manager modules
import helpers
from Manager import Manager
from Logger import Logger
from GenericPlot import GenericPlot


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

        self.messages_list = []


    def load_data_from_storage(self):
        dir_path = _get_directory_path() / STORAGE_DIRECTORY_PATH
        storage = DataStorage(False, dir_path)
        data = storage.read_data()
        data = message.parse_messages(data)
        self.messages_list = data
        print(f"Storage read successful. Stored messages count: {len(data)}")
        if len(data) > 0:
            print(f"Last message: {message.format(data[-1])}\n")


    def plot_data(self):
        self._prepare_manager()

        time_list, temp_list, hum_list = self._reshape_data(self.messages_list)
        self.plot.show_test_plot(time_list, temp_list, hum_list)
        self._run_manager()


    # Create all Measurement Manager instances
    def _prepare_manager(self):
        output_dir = Path('logs') / time.strftime('%Y_%m_%d__%H_%M_%S')
        self.logger = Logger(output_dir / 'system.log')
        self.manager = Manager(output_dir, self.logger)
        self.plot = GenericPlot("Project X", 0, self.logger, self)
        
        self.manager.registerObject(self.plot)


    # Run the manager
    def _run_manager(self):
        self.logger.info("STARTING MANAGER...")
        if self.manager.start():
            helpers.waitToFinish(2)
            self.logger.info("STOPPING MANAGER...")
            self.manager.stop()


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
