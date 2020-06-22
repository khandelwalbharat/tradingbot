
class OrderManager(object):
    """
    Compatible with both types of clients till now, only trades with quantity=1 for now
    """
    def __init__(self, symbol, simulate=False):
        self.symbol = symbol
        self.simulate = simulate #True if running a simulation
        self.order_id = None # ID for main order
        self.stoploss_order_id = None # ID for stoploss order

    def initialize_kite(self, kite_object):
        self.kite = kite_object

    def addTrade(self, time, risk, price, trade_type, stoploss=None, action=None):
        error = ""

        if(not self.simulate):
            
            if(trade_type == 'day_end' or trade_type == 'new' or trade_type == 'trend_reversal'):
            # Place the normal order
                trading_price = int(price // 0.05)*0.05 # Just an approximation for now, patch up later
                transaction_type = self.kite.TRANSACTION_TYPE_BUY if action=='buy' else self.kite.TRANSACTION_TYPE_SELL

                try:
                    self.order_id = self.kite.place_order(tradingsymbol = self.symbol,price=trading_price,quantity=1,variety= self.kite.VARIETY_REGULAR,exchange=self.kite.EXCHANGE_NSE,transaction_type=transaction_type,order_type=self.kite.ORDER_TYPE_LIMIT,product=self.kite.PRODUCT_MIS, validity = self.kite.VALIDITY_DAY)
                except Exception as e:
                    error += e.message
            
            if((trade_type == 'day_end' or trade_type == 'trend_reversal') and self.stoploss_order_id is not None):
            # Cancel the stoploss order
                try:
                    self.kite.cancel_order(variety= self.kite.VARIETY_REGULAR, order_id = self.stoploss_order_id)
                except Exception as e:
                    error += e.message

            if((trade_type == 'new') and stoploss is not None):
            # Place the stoploss order
                stoploss_trading_price = int(stoploss // 0.05)*0.05 # Just an approximation for now, patch up later
                stoploss_transaction_type = self.kite.TRANSACTION_TYPE_BUY if action=='sell' else self.kite.TRANSACTION_TYPE_SELL #Since it is stoploss, do opposite

                try:
                    self.stoploss_order_id = self.kite.place_order(tradingsymbol = self.symbol,price=stoploss_trading_price,quantity=1,variety= self.kite.VARIETY_REGULAR,exchange=self.kite.EXCHANGE_NSE,transaction_type=stoploss_transaction_type,order_type=self.kite.ORDER_TYPE_LIMIT,product=self.kite.PRODUCT_MIS, validity = self.kite.VALIDITY_DAY)
                except Exception as e:
                    error += e.message

        with open("trades.txt", "a+") as f:
            f.write("Added trade for {} at time={} with position={}, price={}, trade_type={}, stoploss={}, order_id = {}, error={}\n".format(self.symbol, time, risk, price, trade_type, stoploss, self.order_id, error))