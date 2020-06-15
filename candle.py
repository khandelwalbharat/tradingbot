import datetime
import numpy as np
import pandas as pd
from copy import deepcopy
from indicator import IndicatorFactory

class CandleEvent(object):

    def __init__(self, symbol, duration, time, O, H, L, C, volume):
        self.symbol = symbol
        self.duration = duration
        self.time = time
        self.O = O
        self.H = H
        self.L = L
        self.C = C
        self.volume = volume
        self.indicators = {}

    def update_indicators(self, indicator_dict):
        self.indicators = deepcopy(indicator_dict)

    def get_df(self):
        dict_ = {'time':self.time, 'O':self.O, 'H':self.H, 'L':self.L, 'C':self.C, 'volume':self.volume}
        dict_.update(self.indicators)
        return pd.DataFrame(dict_, index=[0])


def get_datetime_stripped_to_min(time, rounding=1):
    return datetime.datetime(time.year, time.month, time.day, time.hour, (time.minute // rounding) * rounding)

class CandleGenerator(object):
    """ 
    This is supposed to generate candles of any requisite duration, 
    Doesn’t need to know what symbol it is working on but there will
    Be a unique instance per symbol per duration, also store 
    history of candles, and call indicators to add data
    """

    def __init__(self, symbol, candle_duration, indicators):
        self.O = np.nan
        self.H = np.nan
        self.L = np.nan
        self.C = np.nan
        self.last_volume = 0
        self.volume = 0
        self.symbol = symbol
        self.candles = pd.DataFrame()
        indicator_factory = IndicatorFactory()
        self.indicators = [indicator_factory.load(indicator) for indicator in indicators]
        self.last_time = None
        self.candle_duration = candle_duration
        self.duration = datetime.timedelta(minutes=candle_duration)

    def process_tick(self, symbol_tick):
        if self.last_time is None:
            # first tick
            self.last_time = get_datetime_stripped_to_min(symbol_tick.last_traded_time, self.candle_duration)
            self.O = symbol_tick.last_traded_price
            self.H = symbol_tick.last_traded_price
            self.L = symbol_tick.last_traded_price
            self.C = symbol_tick.last_traded_price
            self.volume = symbol_tick.volume - self.last_volume
            return None
        elif symbol_tick.last_traded_time - self.last_time >= self.duration:
            # tick complete
            candle = CandleEvent(self.symbol, self.candle_duration, self.last_time, self.O, self.H, self.L, self.C, self.volume)
            candles = pd.concat(self.candles, candle.get_df())
            indicator_dict = {}
            [indicator_dict.update(indicator.get_value(candles)) for indicator in self.indicators]
            candle.update_indicators(indicator_dict)

            self.O = symbol_tick.last_traded_price
            self.H = symbol_tick.last_traded_price
            self.L = symbol_tick.last_traded_price
            self.C = symbol_tick.last_traded_price
            self.last_volume = self.last_volume + self.volume
            self.volume = symbol_tick.volume - self.last_volume
            self.candles = pd.concat(self.candles, candle.get_df())
            return candle
        else:
            self.H = max(self.H, symbol_tick.last_traded_price)
            self.L = min(self.L, symbol_tick.last_traded_price)
            self.C = symbol_tick.last_traded_price
            self.volume = symbol_tick.volume - self.last_volume
            return None


class CandleManager(object):
    def __init__(self, symbol):
        self.symbol = symbol
        self.trading_clients = {}
        self.candle_generators = []

    def register_trading_client(self, trading_client):
        candle_duration = trading_client.candle_duration
        self.trading_clients[candle_duration] = self.trading_clients.get(candle_duration, []) + [trading_client]
    
    def create_candle_generators(self):
        for candle_duration, trading_clients in self.trading_clients.items():
            indicators = list(set([indicator for trading_client in trading_clients for indicator in trading_client.indicators]))
            self.candle_generators.append(CandleGenerator(self.symbol, candle_duration, indicators))

    def process_tick(self, symbol_tick):
        for candle_generator in self.candle_generators:
            candle = candle_generator.process_tick(symbol_tick)
            if candle is None:
                continue
            for trading_client in self.trading_clients[candle_generator.candle_duration]:
                trading_client.updateOpinion(candle)
