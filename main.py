#!/usr/bin/env python3

import datetime
import argparse
import logging
from time import sleep

from market_data import MarketDataListener
from trading_client import CrocodileEMACrossoverTradingClient
from candle import CandleManager
from tick import TickManager

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger()

def main(args):
    market_data_listener = MarketDataListener(args.symbol_list, args.api_key, args.request_token, args.api_secret)
    tick_manager = TickManager(market_data_listener.instrument_token_to_symbol)

    for symbol in args.symbol_list:
        trading_client = CrocodileEMACrossoverTradingClient(symbol=symbol, start_time=datetime.time(10, 30), end_time=datetime.time(15, 20))
        candle_manager = CandleManager(symbol)
        candle_manager.register_trading_client(trading_client)
        candle_manager.create_candle_generators()
        tick_manager.register_candle_manager(candle_manager)

    market_data_listener.connect()
    while True:
        market_data_listener.kws.on_ticks = tick_manager.on_ticks

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol_list', nargs='+',help='an integer for the accumulator', required=True)
    parser.add_argument('--api_key', help='API Key, contact developer', required=True)
    parser.add_argument('--api_secret', help='API Secret, contact developer', required=True)
    parser.add_argument('--request_token', help='API request_token, login at https://kite.trade/connect/login?api_key={api_key}&v=3', required=True)
    return parser.parse_args()

if __name__ == "__main__":
    main(get_args())
