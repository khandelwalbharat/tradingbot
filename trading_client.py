from abc import ABC, abstractmethod
import datetime
from order_manager import OrderManager


class TradingClient(ABC):
    
    def __init__(self, symbol, start_time, end_time, candle_duration=5, simulate=False, **kwargs):
        self.symbol = symbol
        self.start_time = start_time
        self.end_time = end_time
        self.candle_duration = candle_duration
        self.simulate = simulate # True if running a simulation
        self.order_manager=OrderManager(symbol = self.symbol, simulate = self.simulate)
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
            return CrocodileEMACrossoverTradingClient(symbol=symbol, start_time=start_time, end_time=end_time, stoploss_fraction=stoploss_fraction, epsilon=epsilon)
        
        elif name == 'OpeningRangeBreakoutTradingClient':
            symbol = kwargs['symbol']
            start_time = str_to_time(kwargs['start_time'])
            end_time = str_to_time(kwargs['end_time'])
            return OpeningRangeBreakoutTradingClient(symbol=symbol, start_time=start_time, end_time=end_time)
        
        else:
            raise Exception("Client {} not implemented".format(name))


class CrocodileEMACrossoverTradingClient(TradingClient):

    def __init__(self, stoploss_fraction=0.01, epsilon=0.001, fast="ema_5", mid="ema_8", slow="ema_13", **kwargs):
        super().__init__(**kwargs)
        # Setting up the arguments
        self.stoploss_fraction = stoploss_fraction
        self.epsilon = epsilon
        self.fast = fast
        self.mid = mid
        self.slow = slow
        self.indicators = [fast, mid, slow]
        
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

        with open("candles/"+self.symbol+".txt", "a+") as f:
            f.write("Time = {}, O = {}, H = {}, L = {}, C = {}, Volume = {}, ema_5={}, ema_8={}, ema_13={}\n".format(time, opeN, high, low, close, candle.volume, fast, mid, slow))

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
        super().__init__(**kwargs)
        
        # Setting up the state variables
        self.position = 0  # 1 for long, 0 for nothing, -1 for short
        self.price = 0  # price at which we are holding the position
        self.stoploss = 0  # stoploss price for the position
        self.high = None
        self.low = None
        self.breakout = False

    def updateOpinion(self, candle):
        # Updates the position according to the candle received and decides if
        # it wants to act on it. If yes, calls self.order_manager
        time = candle.time
        opeN = candle.O
        high = candle.H
        low = candle.L
        close = candle.C
        
        with open("candles/"+self.symbol+".txt", "a+") as f:
            f.write("Time = {}, O = {}, H = {}, L = {}, C = {}, Volume = {}\n".format(time, opeN, high, low, close, candle.volume))

        if(time < self.start_time):  # Ignore starting period
            self.high = high if self.high is None else max(self.high, high)
            self.low = low if self.low is None else min(self.low, low)
            return

        if(self.high is None or self.low is None):
            raise Exception("High/Low for opening range not initialized")

        if self.position == 1:
            # stoploss hit, sell immediately
            if low <= self.stoploss:
                self.order_manager.addTrade(time=time, risk=0, price=self.stoploss, trade_type='stoploss', action = 'sell')
                self.stoploss, self.position = 0, 0
            # square off, or trend changed for buy holding, sell immediately
            elif (time >= self.end_time):
                self.stoploss, self.position = 0, 0
                trade = 'day_end'
                self.order_manager.addTrade(time=time, risk=0, price=close, trade_type=trade, action = 'sell')
        elif self.position == -1:
            # stoploss hit, buy immediately
            if high >= self.stoploss:
                self.order_manager.addTrade(time=time, risk=0, price=self.stoploss, trade_type='stoploss', action = 'buy')
                self.stoploss, self.position = 0, 0
            # square off, or trend changed for sell holding, buy immediately
            elif (time >= self.end_time):
                self.stoploss, self.position = 0, 0
                trade = 'day_end'
                self.order_manager.addTrade(time=time, risk=0, price=close, trade_type=trade, action = 'buy')

        if time >= self.end_time:  # No new action after square off
            assert self.position == 0
            return

        if(close > self.high):
            trend = 1 # Breakout in long position
        elif(close < self.low):
            trend = -1 # Breakout in short position
        else:
            trend = 0

        if(self.position == 0 and (not self.breakout) and trend!=0):
            self.breakout = True
            self.position = trend
            self.stoploss = self.high if self.position==-1 else self.low
            action = 'buy' if trend==1 else 'sell'
            self.order_manager.addTrade(time=time, risk=self.position, price=close, trade_type='new', stoploss=self.stoploss, action=action)
