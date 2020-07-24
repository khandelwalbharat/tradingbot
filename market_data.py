import json
import logging
import pandas as pd
import websocket

class MarketDataListener(object):
    def __init__(self, symbol_list, session_key):
        self.session_key = session_key
        self.headers = {'x-session-token': self.session_key}


        # Only works on NSE symbols for now
        df = pd.read_csv('instruments.csv')
        df = df[(df['tradingsymbol'].isin(symbol_list))]
        self.instrument_token_to_symbol = df.set_index('instrument_token')['tradingsymbol'].to_dict()
        self.symbol_to_instrument_token = df.set_index('tradingsymbol')['instrument_token'].to_dict()
        # self._init_listener()

    # def _init_listener(self):

    def connect(self, tick_manager):

        def on_open(ws):
            instruments_list = list(self.instrument_token_to_symbol.keys())
            instruments_list = [str(x)+"_NSE" for x in instruments_list]
            instruments_list = [{"symbol":x} for x in instruments_list]

            request = {
                "request": {
                    "streaming_type": "quote",
                    "data": {
                        "symbols": instruments_list
                    },
                    "request_type":"subscribe",
                    "response_format":"json"
                }
            }
            ws.send(json.dumps(request))
            ws.send("\n")
            logging.debug("Subscribing to {}".format(instruments_list))

        def on_close(ws):
            # On connection close stop the main loop
            logging.debug("Closing connection with web socket")

        def on_error(ws, error):
            logging.error("Error in web socket with message = {}".format(error))

        def on_message(ws, msg):
            logging.info ("Message Arrived:" + msg)

        self.ws = websocket.WebSocketApp("wss://stream.stocknote.com", on_open = on_open, on_message = on_message, on_error = on_error, on_close = on_close, header = self.headers)

        self.ws.run_forever()