import logging

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger()

class SymbolTickEvent(object):
    """
    Just used to communicated symbol wise ticks from Tick Manager
    to relevant CandleManager
    """
    def __init__(self, instrument_token, timestamp, last_price, volume, oi, average_price, **kwargs):
        self.symbol = instrument_token
        self.last_traded_time = timestamp
        self.last_traded_price = last_price
        self.volume = volume
        self.oi = oi
        self.avg_trade_price = average_price

class TickManager(object):
    def __init__(self, instrument_token_to_symbol_map):
        self.candle_managers = {}
        self.instrument_token_to_symbol = instrument_token_to_symbol_map

    def register_candle_manager(self, candle_manager):
        self.candle_managers[candle_manager.symbol] = candle_manager

    def process_tick(self, ticks):
        for tick in ticks:
            symbol = self.instrument_token_to_symbol[tick['instrument_token']]
            symbol_tick = SymbolTickEvent(symbol, **tick)
            self.candle_managers[symbol_tick.symbol].process_tick(symbol_tick)

    def on_ticks(self, ws, ticks):
        self.process_tick(ticks)
