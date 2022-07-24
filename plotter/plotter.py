from generic_plot import GenericPlot
from enum import Enum

SECONDS_IN_DAY = 60*60*24


class PlotterExceptions(Enum):
    WRONG_ARGS = "Wrong arguments"


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


    def plot_data(self):
        plot = GenericPlot()
        print(f"start: {self.start_date}\nend: {self.end_date}\nperiod: {self.period/SECONDS_IN_DAY}")