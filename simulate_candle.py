import datetime
import numpy as np
import pandas as pd
from copy import deepcopy
from indicator import IndicatorFactory
from candle import CandleEvent, CandleManager
from time import sleep

class SimCandleGenerator(object):
    """ 
    Simulation of the candle generator.
    
    This is supposed to generate candles of any requisite duration, 
    Doesn’t need to know what symbol it is working on but there will
    Be a unique instance per symbol per duration, also store 
    history of candles, and call indicators to add data
    """

    def __init__(self, symbol, candle_duration, indicators):
        self.candles = pd.DataFrame()
        indicator_factory = IndicatorFactory()
        self.indicators = [indicator_factory.load(indicator) for indicator in indicators]
        self.candle_duration = candle_duration
        self.duration = datetime.timedelta(minutes=candle_duration)
        self.symbol = symbol

    def process_candle(self, row):
        if row.empty:
            return None
        candle = CandleEvent(self.symbol, self.candle_duration, row.time.iat[0], row.open.iat[0], row.high.iat[0], row.low.iat[0], row.close.iat[0], row.volume.iat[0])
        self.candles = self.candles.append(candle.get_df())
        self.candles.reset_index(inplace=True, drop=True)
        indicator_dict = {}
        [indicator_dict.update(indicator.get_value(self.candles)) for indicator in self.indicators]
        candle.update_indicators(indicator_dict)
        return candle

def TimeRange(start_time, end_time, delta):
    n=0
    while True:
        time=(datetime.datetime.combine(datetime.date(1,1,1),start_time) + delta*n).time()
        if(time<=end_time):
            yield time
            n+=1
        else:
            return


class SimCandleManager(CandleManager):
    def __init__(self,symbol):
        super().__init__(symbol)
        self.data={}

    def process_tick(self, symbol_tick):
        raise ValueError("Function not found in simulation")

    #Add the day's df of candle data for a particular duration
    def add_data(self, duration, df):
        self.data[duration]=df

    #Similar to process_tick, just that time is a multiple of minutes
    def process_minute(self, time):
        for candle_generator in self.candle_generators:
            day_df=self.data[candle_generator.candle_duration]
            row=day_df.loc[day_df['time']==time]
            candle = candle_generator.process_candle(row)
            if candle is None:
                continue
            for trading_client in self.trading_clients[candle_generator.candle_duration]:
                trading_client.updateOpinion(candle)

    def create_candle_generators(self):
        for candle_duration, trading_clients in self.trading_clients.items():
            indicators = list(set([indicator for trading_client in trading_clients for indicator in trading_client.indicators]))
            self.candle_generators.append(SimCandleGenerator(self.symbol, candle_duration, indicators))

    #Delay is the delay in seconds for each minute of the simulation 
    def simulate_day(self, delay=0.002):
        start_time = datetime.time(9,15,0)
        delta = datetime.timedelta(minutes=1)
        end_time = datetime.time(15,30,0)
        for time in TimeRange(start_time, end_time, delta):
            self.process_minute(time)
            sleep(delay)

