from abc import ABC, abstractmethod
import numpy as np
import ta

class Indicator(ABC):
    @abstractmethod
    def get_value(self, candles):
        """Return indicator value"""
        pass


class IndicatorFactory(object):
    def load(self, name):
        if name.startswith('ema_'):
            duration = int(name.split('ema_')[-1])
            return EMAIndicator(name, duration)
        else:
            raise Exception("Indicator {} not implemented".format(name))


class EMAIndicator(Indicator):
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

    def get_value(self, candles):
        candles_to_use = candles.iloc[-self.duration:]['C']
        emas = np.round(ta.trend.EMAIndicator(candles_to_use, n=self.duration).ema_indicator(), 3)
        return {self.name: emas.iloc[-1]}
