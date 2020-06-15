

class OrderManager(object):
	"""
	Currently a dummy order manager which just prints the orders
	"""
	def __init__(self, symbol):
		self.symbol=symbol
	def addTrade(self, time, risk, price, trade_type, stoploss=None):
		print("Added trade for {} at time={} with position={}, price={}, trade_type={}, stoploss={}".format(self.symbol, time, risk, price, trade_type, stoploss))