#!/usr/bin/env python

import datetime
import asyncio
import argparse
import logging

from market_data import MarketDataListener
from trading_client import CrocodileEMACrossoverTradingClient
from candle import CandleManager
from tick import TickManager

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger()

async def main(args):
    # symbol_list = ['RELIANCE', 'JUSTDIAL', 'SBIN', 'MARUTI']
    tick_event_queue = asyncio.Queue()
    tick_manager = TickManager(tick_event_queue)

    for symbol in args.symbol_list:
        trading_client = CrocodileEMACrossoverTradingClient(symbol=symbol, start_time=datetime.time(10, 30), end_time=datetime.time(15, 20))
        candle_manager = CandleManager(symbol)
        candle_manager.register_trading_client(trading_client)
        candle_manager.create_candle_generators()
        tick_manager.register_candle_manager(candle_manager)

    market_data_listener = MarketDataListener(args.symbol_list, tick_event_queue, args.api_key, args.access_token, args.api_secret)
    market_data_listener.connect()
    await tick_manager.run()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--symbol_list', nargs='+',help='an integer for the accumulator')
    parser.add_argument('-ak', '--api_key', help='API Key, contact developer')
    parser.add_argument('-as', '--api_secret', help='API Secret, contact developer')
    parser.add_argument('-at', '--access_token', help='API access token, login at https://kite.trade/connect/login?api_key={api_key}&v=3')
    return parser.parse_args()

if __name__ == "__main__":
    asyncio.run(main(get_args()))
