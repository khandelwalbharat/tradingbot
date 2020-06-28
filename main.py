#!/usr/bin/env python3

import argparse
import logging
from time import sleep
import json

from market_data import MarketDataListener
from trading_client import TradingClientFactory
from candle import CandleManager
from tick import TickManager
from collections import OrderedDict
import os
from os import path
from utils import get_workdir

def main(args):
    workdir = get_workdir()
    os.makedirs(workdir, exist_ok=True)

    logging.basicConfig(level=logging.DEBUG, filename=path.join(workdir, 'log.txt'), format='%(asctime)s - %(levelname)s - %(message)s')

    with open(args.portfolio_file, 'r') as f:
        portfolio = json.load(f)
    
    client_factory = TradingClientFactory()

    candle_manager_dict = {} #Contains mapping from symbol to its candle manager to prevent duplication of candle managers for clients of same symbol
    symbol_list = []
    clients = []

    for client in portfolio:
        symbol = client['symbol']
        if(symbol not in symbol_list):
            symbol_list.append(symbol)
        trading_client = client_factory.load(client['Name'], **OrderedDict(client))
        clients.append(trading_client)

        if(symbol not in candle_manager_dict):
            candle_manager = CandleManager(symbol)
            candle_manager_dict[symbol] = candle_manager
        else:
            candle_manager = candle_manager_dict[symbol]
        candle_manager.register_trading_client(trading_client)

    market_data_listener = MarketDataListener(symbol_list, args.api_key, args.request_token, args.api_secret)
    tick_manager = TickManager(market_data_listener.instrument_token_to_symbol)
        
    for client in clients:
        client.order_manager.initialize_kite(market_data_listener.kite)

    for symbol, candle_manager in candle_manager_dict.items():
        candle_manager.create_candle_generators()
        tick_manager.register_candle_manager(candle_manager)

    market_data_listener.connect()
    while True:
        market_data_listener.kws.on_ticks = tick_manager.on_ticks

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--portfolio_file',help='give the json file having the portfolio to be traded on', required=True)
    parser.add_argument('--api_key', help='API Key, contact developer', required=True)
    parser.add_argument('--api_secret', help='API Secret, contact developer', required=True)
    parser.add_argument('--request_token', help='API request_token, login at https://kite.trade/connect/login?api_key={api_key}&v=3', required=True)
    return parser.parse_args()

if __name__ == "__main__":
    main(get_args())
