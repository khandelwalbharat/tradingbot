import logging

class OrderManager(object):
    """
    Compatible with both types of clients till now, only trades with quantity=1 for now
    """
    def __init__(self, symbol, name, simulate=False):
        self.symbol = symbol
        self.client_name = name
        self.simulate = simulate #True if running a simulation
        self.order_id = None # ID for main order
        self.stoploss_order_id = None # ID for stoploss order
        self.kite = None

    def initialize_kite(self, kite_object):
        self.kite = kite_object

    def addTrade(self, time, risk, price, trade_type, stoploss=None, action=None, quantity=1):
        if(self.kite is None and (not self.simulate)):
            logging.error('Kite not initialized in {} for {}'.format(self.client_name, self.symbol))

        action = 'buy' if risk == 1 else 'sell'
        # Safeguard against large quantity by mistake
        if(quantity != 1):
            logging.critical('Quantity = {} in {} for {}'.format(quantity, self.client_name, self.symbol))

        elif(trade_type == 'new' and stoploss is None):
            logging.error('No stoploss specified in trade {} for {}'.format(self.client_name, self.symbol))

        if(not self.simulate):            
            if(trade_type == 'day_end' or trade_type == 'new' or trade_type == 'trend_reversal'):
            # Place the normal order
                trading_price = round(price / 0.05) * 0.05 # Just an approximation for now, patch up later
                transaction_type = self.kite.TRANSACTION_TYPE_BUY if action=='buy' else self.kite.TRANSACTION_TYPE_SELL

                try:
                    self.order_id = self.kite.place_order(tradingsymbol = self.symbol,price=trading_price,quantity=quantity,variety= self.kite.VARIETY_REGULAR,exchange=self.kite.EXCHANGE_NSE,transaction_type=transaction_type,order_type=self.kite.ORDER_TYPE_LIMIT,product=self.kite.PRODUCT_MIS, validity = self.kite.VALIDITY_DAY)
                    logging.info('Order: {} placed {} {} @ {} and quantity = {} with order_id = {}'.format(self.client_name, self.symbol, action, trading_price, quantity, self.order_id))
                except Exception as e:
                    logging.error('Order: {} failed to place {} {} @ {} and quantity = {} with message = {}'.format(self.client_name, self.symbol, action, trading_price, quantity, e.message), exc_info=True)
                    
            if((trade_type == 'day_end' or trade_type == 'trend_reversal') and self.stoploss_order_id is not None):
            # Cancel the stoploss order
                try:
                    self.kite.cancel_order(variety= self.kite.VARIETY_REGULAR, order_id = self.stoploss_order_id)
                    logging.info('Order: Stoploss order cancelled by {} for {} with order_id = {}'.format(self.client_name, self.symbol, self.stoploss_order_id))
                except Exception as e:
                    logging.error('Order: {} on {} failed to cancel stoploss order with message = {}'.format(self.client_name, self.symbol, e.message), exc_info=True)
                    

            if((trade_type == 'new') and stoploss is not None):
            # Place the stoploss order
                
                stoploss_trading_price = round(stoploss / 0.05) * 0.05 # Just an approximation for now, patch up later
                stoploss_transaction_type = self.kite.TRANSACTION_TYPE_BUY if action=='sell' else self.kite.TRANSACTION_TYPE_SELL #Since it is stoploss, do opposite
                offset = 0.0002*stoploss
                if(action == 'buy'): #the stoploss is selling
                    stoploss_trigger_price = stoploss+offset
                    stoploss_trigger_price = round(stoploss_trigger_price / 0.05) * 0.05
                    stoploss_trigger_price = max(stoploss_trigger_price, stoploss_trading_price+0.05)
                elif(action == 'sell'): #stoploss is buying
                    stoploss_trigger_price = stoploss-offset
                    stoploss_trigger_price = round(stoploss_trigger_price / 0.05) * 0.05
                    stoploss_trigger_price = min(stoploss_trigger_price, stoploss_trading_price-0.05)

                try:
                    self.stoploss_order_id = self.kite.place_order(tradingsymbol = self.symbol,price=stoploss_trading_price,trigger_price = stoploss_trigger_price, quantity=quantity,variety= self.kite.VARIETY_REGULAR,exchange=self.kite.EXCHANGE_NSE,transaction_type=stoploss_transaction_type,order_type=self.kite.ORDER_TYPE_SL,product=self.kite.PRODUCT_MIS, validity = self.kite.VALIDITY_DAY)
                    logging.info('Order: {} placed stoploss order {} {} @ {} and quantity = {} with trigger_price = {} and order_id = {}'.format(self.client_name, self.symbol, action, stoploss_trading_price, quantity, stoploss_trigger_price, self.stoploss_order_id))
                except Exception as e:
                    logging.error('Order: {} failed to place stoploss order {} {} @ {} and quantity = {} with trigger_price = {} and message = {}'.format(self.client_name, self.symbol, action, stoploss_trading_price, quantity, stoploss_trigger_price, e.message), exc_info=True)

        if(self.simulate):
            logging.debug("Order: {} simulator added trade for {} at time={} with position={}, price={}, trade_type={}, stoploss={}".format(self.client_name, self.symbol, time, risk, price, trade_type, stoploss))