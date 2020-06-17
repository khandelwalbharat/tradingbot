

class OrderManager(object):
    """
    Currently a dummy order manager which just prints the orders
    """
    def __init__(self, symbol):
        self.symbol=symbol
    def addTrade(self, time, risk, price, trade_type, stoploss=None):
        with open("trades.txt", "a+") as f:
            f.write("Added trade for {} at time={} with position={}, price={}, trade_type={}, stoploss={}\n".format(self.symbol, time, risk, price, trade_type, stoploss))
