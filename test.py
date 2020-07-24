#!/usr/bin/env python3

import websocket

def on_message(ws, msg):
    print ("Message Arrived:" + msg)
    
def on_error(ws, error):
    print (error)

def on_close(ws):
    print ("Connection Closed")

def on_open(ws):
    print ("Sending json")
    data='{"request":{"streaming_type":"quote", "data":{"symbols":[{"symbol":"16852_NSE"}, {"symbol":"16852_NSE"}]}, "request_type":"subscribe", "response_format":"json"}}'
    ws.send(data)
    ws.send("\n")

headers = {'x-session-token': 'fb95da11b2471e029be9e4a653944f41'}

websocket.enableTrace(True)

ws = websocket.WebSocketApp("wss://stream.stocknote.com", on_open = on_open, on_message = on_message, on_error = on_error, on_close = on_close, header = headers)

ws.run_forever()