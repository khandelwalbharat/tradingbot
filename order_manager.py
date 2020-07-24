import logging
from samco import SamcoOrderExecutor

class OrderManager(object):
    """
    Compatible with both types of clients till now, only trades with quantity=1 for now
    """
    def __init__(self, symbol, name, quantity, simulate=False):
        self.symbol = symbol
        self.client_name = name
        self.simulate = simulate #True if running a simulation
        self.order_id = None # ID for main order
        self.stoploss_order_id = None # ID for stoploss order
        self.quantity = quantity
        self.samco = None #it stands for a Samco order manager
        
    def initialize_samco(self, samco_object):
        self.samco = samco_object

    def addORBTrade(self, time, price, action):
        trigger_price = round(price / 0.05) * 0.05 # Just an approximation for now, patch up later
        transaction_type = 'BUY' if action=='buy' else 'SELL'
        offset = 0.0002*price
        
        if(action == 'buy'):
            trading_price = price+offset
            trading_price = round(trading_price / 0.05) * 0.05
            trading_price = max(trading_price, trigger_price+0.05)

        elif(action == 'sell'):
            trading_price = price-offset
            trading_price = round(trading_price / 0.05) * 0.05
            trading_price = min(trading_price, trigger_price-0.05)
            
        try:
            self.order_id = self.samco.place_order(tradingsymbol = self.symbol,price=trading_price,trigger_price = trigger_price, quantity=self.quantity,transaction_type=transaction_type,order_type='SL')
            logging.info('Order: {} placed trigger order {} {} @ {} and quantity = {} with trigger_price = {} and order_id = {}'.format(self.client_name, self.symbol, action, trading_price, self.quantity, trigger_price, self.order_id))
        except Exception as e:
            logging.error('Order: {} failed to place trigger order {} {} @ {} and quantity = {} with trigger_price = {} and message = {}'.format(self.client_name, self.symbol, action, trading_price, self.quantity, trigger_price, e), exc_info=True)
            try:
                self.order_id = self.samco.place_order(tradingsymbol = self.symbol,price=trading_price, quantity=self.quantity,transaction_type=transaction_type,order_type='L')
                logging.info('Order: {} placed limit order {} {} @ {} and quantity = {} with order_id = {}'.format(self.client_name, self.symbol, action, trading_price, self.quantity, self.order_id))
            except Exception as e:
                logging.error('Order: {} failed to place limit order {} {} @ {} and quantity = {} with message = {}'.format(self.client_name, self.symbol, action, trading_price, self.quantity, e), exc_info=True)
