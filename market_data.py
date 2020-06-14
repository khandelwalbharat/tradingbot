from kiteconnect import KiteTicker, KiteConnect
import logging
import pandas as pd

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger()

class MarketDataListener(object):
    def __init__(self, symbol_list, tick_event_queue, API_key, API_access_token, API_secret):
        self.API_key = API_key
        self.API_secret = API_secret
        self.API_access_token = API_access_token
        
        self.tick_event_queue = tick_event_queue
        self.kite = KiteConnect(api_key=self.API_key)
        data = self.kite.generate_session(self.API_access_token, api_secret=self.API_secret)
        self.kite.set_access_token(data["access_token"])

        df = pd.DataFrame(self.kite.instruments())
        df = df[(df['tradingsymbol'].isin(symbol_list)) & (df['segment'] == 'NSE')]
        self.instrument_token_to_symbol_map = df.set_index('instrument_token')['tradingsymbol'].to_dict()
        self.symbol_to_instrument_token_map = df.set_index('tradingsymbol')['instrument_token'].to_dict()
        self._init_listener()

    def _init_listener(self):
        # Initialise
        kws = KiteTicker(self.API_key, self.API_access_token)

        def on_ticks(ws, ticks):
            # Callback to receive ticks.
            self.tick_event_queue.put(ticks)

        def on_connect(ws, response):
            # Callback on successful connect.
            # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
            ws.subscribe(self.instrument_token_to_symbol_map.keys())

            # Set RELIANCE to tick in `full` mode.
            ws.set_mode(ws.MODE_FULL, self.instrument_token_to_symbol_map.keys())

        def on_close(ws, code, reason):
            # On connection close stop the main loop
            # Reconnection will not happen after executing `ws.stop()`
            ws.stop()

        # Assign the callbacks.
        kws.on_ticks = on_ticks
        kws.on_connect = on_connect
        kws.on_close = on_close
        self.kws = kws

    def connect(self):
        # Infinite loop on the main thread. Nothing after this will run.
        # You have to use the pre-defined callbacks to manage subscriptions.
        self.kws.connect(threaded=True)
