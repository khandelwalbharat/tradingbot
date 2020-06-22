#!/usr/bin/env python3

import datetime
import argparse
import logging
from time import sleep
import os
from trading_client import CrocodileEMACrossoverTradingClient
from simulate_candle import SimCandleManager
import pandas as pd

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger()

def main(args):
    for symbol in args.symbol_list:
        trading_client = CrocodileEMACrossoverTradingClient(symbol=symbol, start_time=datetime.time(10, 30), end_time=datetime.time(15, 20), simulate=True)
        candle_manager = SimCandleManager(symbol)
        candle_manager.register_trading_client(trading_client)
        candle_manager.create_candle_generators()
        for folder in os.listdir(args.data_path):
            duration = int(folder.split("minute")[0])
            data=pd.read_csv(os.path.join(args.data_path, folder, symbol+".csv"))
            data['timestamp'] = pd.to_datetime(data['date'])
            data['time'] = data['timestamp'].dt.time
            data['date'] = data['timestamp'].dt.date
            day_df=data.loc[data['date']==datetime.datetime.strptime(args.date, '%d-%m-%Y').date()]
            candle_manager.add_data(duration, day_df)
            candle_manager.simulate_day(delay=0)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol_list', nargs='+',help='an integer for the accumulator')
    parser.add_argument('--date', help='date in DD-MM-YYYY format')
    parser.add_argument('--data_path', help='complete path of the data folder')
    return parser.parse_args()

if __name__ == "__main__":
    main(get_args())
