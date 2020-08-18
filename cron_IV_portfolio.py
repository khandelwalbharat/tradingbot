import numpy as np
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import time
import json
import datetime

def candles_to_start_time(num_candles):
    return (datetime.datetime.combine(datetime.date.today(), datetime.time(9, 10, 0))+datetime.timedelta(minutes=5*num_candles)).time()

portfolio = []

class ParseTables:
    def __init__(self, *args, **kwargs):
        self.schema = float
        self.bs = kwargs.get('soup')
        self.numCols = kwargs.get('numColumns')
        self._parse()

    def _parse(self):
        trs = self.bs.find_all('tr')
        lists = []
        schema = self.schema
        for tr in trs:
            tds = tr.find_all('td')
            if(len(tds)==self.numCols):
                lst = []
                for i in range(0, len(tds)):
                    if(i<len(tds)-1):
                        txt = tds[i].text.replace('\n','').replace(' ','').replace(',','')
                        try:
                            val = self.schema(txt)
                        except:
                            val = str(txt)
                    else:
                        match = re.search("ViewOptionChain/([^\s^\/]+)/", str(tds[i]))
                        stock_id = match.group(1)
                        val = stock_id.replace("&amp;", "&")
                    lst.append(val)
                lists.append(lst)
        self.lists = lists

    def get_tables(self):
        return self.lists

    def get_df(self):
        return pd.DataFrame(self.lists)

def get_volatility_data(option_type):
    url="https://www.topstockresearch.com/FnO/{}Options/HighIV{}OptionNearMonthExpiryDate.html".format(option_type, option_type)
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.google.com/'})
    c = r.content
    soup = BeautifulSoup(c)
    tables = soup.findAll("table")
    options_table=tables[1]
    tp = ParseTables(soup=options_table, numColumns = 12)
    options_df = tp.get_df()
    options_col = ['name', 'spot_px', 'strike_px', 'IV'] + list(range(3,10))+['symbol']
    options_df.set_axis(options_col, axis='columns', inplace=True)
    options_df = options_df[['symbol', 'spot_px', 'strike_px', 'IV']]
    options_df = options_df[options_df['symbol']!='BANKNIFTY']
    options_df['distance'] = (options_df['spot_px']-options_df['strike_px']).abs()
    disp_df = options_df.sort_values('distance', ascending=True).groupby('symbol').head(1)
    disp_df.sort_values('IV', ascending=False, inplace=True)
    disp_df = disp_df.loc[disp_df['spot_px']>100]
    disp_df = disp_df.loc[disp_df['distance']<0.15*disp_df['spot_px']]
    return disp_df

put_df = get_volatility_data('Put')
time.sleep(5)

call_df = get_volatility_data('Call')

option_df = pd.merge(left = put_df, right = call_df, left_on = 'symbol', right_on = 'symbol')

option_df['Average_IV'] = (option_df['IV_x']+option_df['IV_y'])/2
option_df.sort_values('Average_IV', ascending=False, inplace=True)
option_df = option_df[['symbol', 'spot_px_x', 'Average_IV']]

capital = 60000
orb_symbols = {}
for i in range(min(5, len(option_df))):
    symbol = option_df['symbol'].iat[i]
    px = option_df['spot_px_x'].iat[i]
    quantity = int(round(capital/px))
    orb_symbols[symbol] = (12, quantity)

for symbol, (candle,quantity) in orb_symbols.items():
    portfolio.append(symbol)

import datetime
import getpass
import os

def get_today_date_string():
    now = datetime.datetime.now()
    dt_string = now.strftime("%Y%m%d")
    return dt_string

def get_workdir():
    workdir = "/home/{}/spare/local/tradingbot/IV/".format(getpass.getuser())
    return workdir

workdir = get_workdir()
date = get_today_date_string()
os.makedirs(workdir, exist_ok=True)

with open(workdir+'{}.json'.format(date), 'w') as f:
    json.dump(portfolio, f, default = str)
