from abc import ABC, abstractmethod
import datetime
from order_manager import OrderManager
import logging


class TradingClient(ABC):
    
    def __init__(self, symbol, start_time, end_time, name, candle_duration=5, simulate=False, quantity = 1, **kwargs):
        self.name = name # Name of the client, not symbol
        self.symbol = symbol
        self.start_time = start_time
        self.end_time = end_time
        self.candle_duration = candle_duration
        self.simulate = simulate # True if running a simulation
        self.quantity = quantity       
        self.order_manager=OrderManager(symbol = self.symbol, simulate = self.simulate, name = self.name, quantity = self.quantity)
        self.indicators = []

    @abstractmethod
    def updateOpinion(self, candle):
        pass

def str_to_time(time_str):
    return datetime.datetime.strptime(time_str, '%H:%M:%S').time()

class TradingClientFactory(object):
   
    def load(self, name, **kwargs):

        if name == 'CrocodileEMACrossoverTradingClient':
            symbol = kwargs['symbol']
            start_time = str_to_time(kwargs['start_time'])
            end_time = str_to_time(kwargs['end_time'])
            epsilon = kwargs['epsilon']
            stoploss_fraction = kwargs['stoploss_fraction']
            quantity = kwargs['quantity']
            return CrocodileEMACrossoverTradingClient(symbol=symbol, start_time=start_time, end_time=end_time, stoploss_fraction=stoploss_fraction,\
                epsilon=epsilon, quantity = quantity)
        
        elif name == 'OpeningRangeBreakoutTradingClient':
            symbol = kwargs['symbol']
            start_time = str_to_time(kwargs['start_time'])
            end_time = str_to_time(kwargs['end_time'])
            quantity = kwargs['quantity']
            return OpeningRangeBreakoutTradingClient(symbol=symbol, start_time=start_time, end_time=end_time, quantity = quantity)
        
        else:
            logging.error("Client {} not implemented".format(name))
            raise Exception("Client {} not implemented".format(name))



#ONE MAJOR THING LEFT IN IMPLEMENTATION OF ORDER MANAGER FOR THIS, setting up action values, don't use unless patched.
class CrocodileEMACrossoverTradingClient(TradingClient):

    def __init__(self, stoploss_fraction=0.01, epsilon=0.001, fast="ema_5", mid="ema_8", slow="ema_13", **kwargs):
        super().__init__(name = 'Crocodile Client', **kwargs)
        # Setting up the arguments

        self.stoploss_fraction = stoploss_fraction
        self.epsilon = epsilon
        self.fast = fast
        self.mid = mid
        self.slow = slow
        self.indicators = [fast, mid, slow]
        
        logging.info('Client: Initialized {} on {} with stoploss_fraction = {}, epsilon = {}, start_time = {}, end_time = {}'.format(self.name, \
            self.symbol, self.stoploss_fraction, self.epsilon, self.start_time, self.end_time))

        # Setting up the state variables
        self.position = 0  # 1 for long, 0 for nothing, -1 for short
        self.price = 0  # price at which we are holding the position
        self.stoploss = 0  # stoploss price for the position
        self.blocked_direction_stoploss = 0

    def updateOpinion(self, candle):
        # Updates the position according to the candle received and decides if
        # it wants to act on it. If yes, calls self.order_manager
        time = candle.time
        opeN = candle.O
        high = candle.H
        low = candle.L
        close = candle.C
        fast = candle.indicators[self.fast]
        mid = candle.indicators[self.mid]
        slow = candle.indicators[self.slow]

        mild_trend = 0
        if((fast - mid > 0) and (mid - slow > 0)):
            mild_trend = 1
        elif((mid - fast > 0) and (slow - mid > 0)):
            mild_trend = -1

        trend = 0
        if (fast - mid >= self.epsilon * close) and (mid - slow >= self.epsilon * close):
            trend = 1
        elif (mid - fast >= self.epsilon * close) and (slow - mid >= self.epsilon * close):
            trend = -1

        if time < self.start_time:  # Ignore starting period
            return
        if self.position == 1:
            # stoploss hit, sell immediately
            if low <= self.stoploss:
                self.order_manager.addTrade(
                    time=time, risk=0, price=self.stoploss, trade_type='stoploss')
                self.stoploss, self.position = 0, 0
                self.blocked_direction_stoploss = 1
            # square off, or trend changed for buy holding, sell immediately
            elif (time >= self.end_time or mild_trend == -1):
                self.stoploss, self.position = 0, 0
                trade = 'day_end' if time >= self.end_time else 'trend_reversal'
                self.order_manager.addTrade(time=time, risk=0, price=close, trade_type=trade)
                self.blocked_direction_stoploss = 0
        elif self.position == -1:
            # stoploss hit, buy immediately
            if high >= self.stoploss:
                self.order_manager.addTrade(time=time, risk=0, price=self.stoploss, trade_type='stoploss')
                self.stoploss, self.position = 0, 0
                self.blocked_direction_stoploss = -1
            # square off, or trend changed for sell holding, buy immediately
            elif (time >= self.end_time or mild_trend == 1):
                self.stoploss, self.position = 0, 0
                trade = 'day_end' if time >= self.end_time else 'trend_reversal'
                self.order_manager.addTrade(time=time, risk=0, price=close, trade_type=trade)
                self.blocked_direction_stoploss = 0

        if time >= self.end_time:  # No new action after square off
            assert self.position == 0
            return

        if self.position == 0 and self.blocked_direction_stoploss != trend and trend != 0:
            self.position = trend
            self.stoploss = close * (1 - trend * self.stoploss_fraction)
            self.order_manager.addTrade(time=time, risk=self.position, price=close, trade_type='new', stoploss=self.stoploss)
            self.blocked_direction_stoploss = 0


class OpeningRangeBreakoutTradingClient(TradingClient):

    def __init__(self, **kwargs):
        super().__init__(name = 'ORB Client', **kwargs)
        
        # Setting up the state variables
        self.high = None
        self.low = None

        logging.info('Client: Initialized {} on {} with start_time = {}, end_time = {}'.format(self.name, \
            self.symbol, self.start_time, self.end_time))

        
    def updateOpinion(self, candle):
        # Updates the position according to the candle received and decides if
        # it wants to act on it. If yes, calls self.order_manager
        time = candle.time
        opeN = candle.O
        high = candle.H
        low = candle.L
        close = candle.C

        # ignore candles before 9:15
        if(time < datetime.time(9,15)):
            return

        if(time <= self.start_time):  # Ignore starting period
            self.high = high if self.high is None else max(self.high, high)
            self.low = low if self.low is None else min(self.low, low)

        # if(self.high is None or self.low is None):
        #     logging.error("High/Low for opening range not initialized in {} for {}".format(self.name, self.symbol))
        #     raise Exception("High/Low for opening range not initialized")

        # Can improve later to handle connection failure issues, good for now
        if(time == self.start_time):
            self.order_manager.addORBTrade(time=time, price=self.high, action='buy')
            self.order_manager.addORBTrade(time=time, price=self.low, action='sell')
            