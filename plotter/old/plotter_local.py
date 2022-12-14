from enum import Enum
from pathlib import Path
import time
import matplotlib.dates as md
import datetime as dt
import environment
environment.add_internal_sources_to_path()

import message
from data_storage import DataStorage

import managerHelpers
from Manager import Manager
from Logger import Logger
from GenericPlotBase import *


#####################################################################
#                    Not config, don't change
#####################################################################

# path to storage directory, where all ProjectX data and backups are stored
STORAGE_DIRECTORY_PATH = "../binaries"

SECONDS_IN_DAY = 60*60*24


#####################################################################
#                    Project X Plot class
#####################################################################

class ProjectXPlot(GenericPlotBase):
    def __init__(self, id: int, loggerInstance: any):
        """Generic Plot device initializtion."""
        GenericPlotBase.__init__(self, "Project X", id, loggerInstance, 
                sensorInstance = None, channelsCount = 2,
                runConfiguration = False)

    def configureAll(self):
        plotSize = PlotSize()
        plotMargin = PlotMargin()
        self.configPlot("Project X", rowCount = 2, colCount = 1, size = plotSize, margin = plotMargin)

        xLabelFormatter = md.DateFormatter('%d.%m %H:%M')
        xValueFormatter = dt.datetime.fromtimestamp
        tempConfig = SubplotConfig(xLabel = "Timestamp", yLabel = "Temperature [*C]",
            xLabelFormatter = xLabelFormatter, xValueFormatter = xValueFormatter,
            serie = SubplotSerie())
        tempSubplot = self.addSubplot(tempConfig)

        humConfig = SubplotConfig(xLabel = "Timestamp", yLabel = "Humidity [% RH]",
            xLabelFormatter = xLabelFormatter, xValueFormatter = xValueFormatter,
            serie = SubplotSerie())
        humSubplot = self.addSubplot(humConfig)

        return tempSubplot, humSubplot


#####################################################################
#                   Project X plotting class
#####################################################################

class Plotter():
    def __init__(self, start_date: int = None, 
                 end_date: int = None, 
                 duration: float = 7.0):
        try:
            period = round(duration * SECONDS_IN_DAY)
            if end_date == None:
                if start_date == None:
                    end_date = int(time.time())
                else:
                    end_date = start_date + period
            if start_date == None:
                start_date = end_date - period
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
        dir_path = environment.get_directory_path() / STORAGE_DIRECTORY_PATH
        storage = DataStorage(False, dir_path)
        data = storage.read_all_data()
        data = message.parse_messages(data)
        self.messages_list = data
        print(f"Storage read successful. Stored messages count: {len(data)}")
        if len(data) > 0:
            print(f"Last message: {message.format(data[-1])}\n")


    def plot_data(self):
        self._prepare_manager()
        time_list, temp_list, hum_list = self._reshape_data(self.messages_list)
        tempSubplot, humSubplot = self.plot.configureAll()
        self.plot.formatAppendData(time_list, temp_list, tempSubplot)
        self.plot.formatAppendData(time_list, hum_list, humSubplot)
        self.plot.show()
        self._run_manager()


    # Create all Measurement Manager instances
    def _prepare_manager(self):
        output_dir = Path('logs') / time.strftime('%Y_%m_%d__%H_%M_%S')
        self.logger = Logger(output_dir / 'system.log')
        self.manager = Manager(output_dir, self.logger)
        self.plot = ProjectXPlot(0, self.logger)
        self.manager.registerObject(self.plot)


    # Run the manager
    def _run_manager(self):
        self.logger.info("STARTING MANAGER...")
        if self.manager.start():
            managerHelpers.waitToFinish(1)
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
