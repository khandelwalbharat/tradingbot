import logging
import json
import datetime

class SymbolTickEvent(object):
    """
    Just used to communicated symbol wise ticks from Tick Manager
    to relevant CandleManager
    """
    def __init__(self, symbol, sym, lTrdT, ltp, vol, oI, avgPr, **kwargs):
        self.symbol = symbol
        self.instrument_token = sym
        self.last_traded_time = datetime.datetime.strptime(lTrdT, '%d %b %Y, %I:%M:%S %p')
        self.last_traded_price = float(ltp)
        self.volume = int(vol)
        # self.oi = int(oi)
        self.avg_trade_price = float(avgPr)

class TickManager(object):
    def __init__(self, instrument_token_to_symbol_map):
        self.candle_managers = {}
        self.instrument_token_to_symbol = instrument_token_to_symbol_map

    def register_candle_manager(self, candle_manager):
        self.candle_managers[candle_manager.symbol] = candle_manager

    def process_tick(self, ticks):
        tick = ticks['response']['data']
        symbol = self.instrument_token_to_symbol[int(tick['sym'].split('_')[0])]
        # print(symbol)
        symbol_tick = SymbolTickEvent(symbol, **tick)
        self.candle_managers[symbol_tick.symbol].process_tick(symbol_tick)

    def on_ticks(self, ticks):
        ticks = json.loads(ticks)
        # print(ticks)
        # logging.info("Ticks: {}".format(ticks))
        self.process_tick(ticks)
