from kiteconnect import KiteTicker, KiteConnect
import logging
import pandas as pd

class MarketDataListener(object):
    def __init__(self, symbol_list, API_key, API_request_token, API_secret):
        self.API_key = API_key
        self.API_secret = API_secret
        self.API_request_token = API_request_token
        
        self.kite = KiteConnect(api_key=self.API_key)
        data = self.kite.generate_session(self.API_request_token, api_secret=self.API_secret)
        self.access_token = data["access_token"]
        self.kite.set_access_token(self.access_token)

        df = pd.DataFrame(self.kite.instruments())
        df = df[(df['tradingsymbol'].isin(symbol_list)) & (df['segment'] == 'NSE')]
        self.instrument_token_to_symbol = df.set_index('instrument_token')['tradingsymbol'].to_dict()
        self.symbol_to_instrument_token = df.set_index('tradingsymbol')['instrument_token'].to_dict()
        self._init_listener()

    def _init_listener(self):
        # Initialise
        kws = KiteTicker(self.API_key, self.access_token, debug=True)

        def on_ticks(ws, ticks):
            # Callback to receive ticks.
            pass

        def on_connect(ws, response):
            # Callback on successful connect.
            # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
            symbol_list = list(self.instrument_token_to_symbol.keys())
            logging.debug("Subscribing to {}".format(symbol_list))
            ws.subscribe(symbol_list)

            # Set RELIANCE to tick in `full` mode.
            ws.set_mode(ws.MODE_FULL, symbol_list)

        def on_close(ws, code, reason):
            # On connection close stop the main loop
            # Reconnection will not happen after executing `ws.stop()`
            logging.debug("Closing connection with host with code = {} and reason = {}".format(code, reason))

        # Assign the callbacks.
        kws.on_ticks = on_ticks
        kws.on_connect = on_connect
        kws.on_close = on_close
        self.kws = kws

    def connect(self):
        # Infinite loop on the main thread. Nothing after this will run.
        # You have to use the pre-defined callbacks to manage subscriptions.
        self.kws.connect(threaded=True)
