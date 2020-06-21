#Generates a portfolio.json file and dumps the portfolio in it

import json
import datetime

def candles_to_start_time(num_candles):
    return (datetime.datetime.combine(datetime.date.today(), datetime.time(9, 15, 0))+datetime.timedelta(minutes=5*num_candles)).time()

portfolio = []

#Add the Opening Range Breakout Clients to the portfolio
orb_symbols = {'EICHERMOT':4, 'BANDHANBNK':6, 'MARUTI':8, 'MRF':10, 'JUSTDIAL':8}

for symbol, candle in orb_symbols.items():
    portfolio.append({'Name':'OpeningRangeBreakoutTradingClient', 'symbol':symbol, 'start_time':candles_to_start_time(candle), 'end_time':datetime.time(15, 20, 0)})


#Add the Crocodile Clients to the portfolio
crocodile_symbols = {'EICHERMOT':0.00025, 'BANDHANBNK':0.0005 , 'MARUTI':0.00025 , 'SBIN':0.0005 , 'TATASTEEL':0.0005}

for symbol, epsilon in crocodile_symbols.items():
    portfolio.append({'Name':'CrocodileEMACrossoverTradingClient', 'symbol':symbol, 'start_time':datetime.time(10, 30), 'end_time':datetime.time(15, 20, 0), 'epsilon':epsilon, 'stoploss_fraction':0.01})

with open('portfolio.json', 'w') as f:
    json.dump(portfolio, f, default = str)