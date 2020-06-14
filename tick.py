import logging

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger()

class TradeUnit(object):
    def __init__(self, symbol, instrument_token):
        self.symbol = symbol
        self.instrument_token = symbol_to_instrument_token(symbol)

class SymbolTickEvent(object):
    """
    Just used to communicated symbol wise ticks from Tick Manager
    to relevant CandleManager
    """
    def __init__(self, instrument_token, last_traded_time, last_traded_price, volume, oi, avg_trade_price):
        self.symbol = instrument_token_to_symbol(instrument_token)
        self.last_traded_time = last_traded_time
        self.last_traded_price = last_traded_price
        self.volume = volume
        self.oi = oi
        self.avg_trade_price = avg_trade_price

class TickManager(object):
    def __init__(self, tick_event_queue):
        self.candle_managers = {}
        self.tick_event_queue = tick_event_queue

    def register_candle_manager(self, candle_manager):
        self.candle_managers[candle_manager.symbol] = candle_manager

    def process_tick(self, ticks):
        for tick in ticks:
            symbol_tick = SymbolTickEvent(tick['instrument_token'], tick['timestamp'], tick['last_price'], tick['volume'], tick['oi'], tick['average_price'])
            self.candle_managers[symbol_tick.symbol].process_tick(symbol_tick)

    async def run(self):
        while True:
            ticks = await self.tick_event_queue.get()
            self.process_tick(ticks)
            print("RUNNING")
