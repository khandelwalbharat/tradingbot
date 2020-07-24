import requests
import json

class SamcoOrderExecutor(object):
    """
    Provides the API interface for placing orders in Samco
    Beware: Currently some settings in terms of default arguments might be meant for ORB or intraday strategies
    """
    def __init__(self, session_key):
        self.session_key = session_key
        self.headers = {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'x-session-token': self.session_key
        }

    def place_order(tradingsymbol, transaction_type, order_type, exchange='NSE', quantity=1, price=None, trigger_price=None, product='MIS', validity='DAY'):
        raise Exception("Orders Blocked") #Testing phase

        # Convert the floats, int into strings first
        quantity = str(quantity)
        price = str(price)
        trigger_price = str(trigger_price)

        requestBody={
          "symbolName": tradingsymbol,
          "exchange": exchange,
          "transactionType": transaction_type,
          "orderType": order_type,
          "quantity": quantity,
          "disclosedQuantity": quantity,
          "price": price,
          "priceType": "LTP", #Only for BO orders, doesnt matter
          "marketProtection": "--", #Default
          "orderValidity": validity,
          "afterMarketOrderFlag": "NO", #By default
          "productType": product,
          "triggerPrice": trigger_price
        }

        r = requests.post('https://api.stocknote.com/order/placeOrder', data=json.dumps(requestBody), headers = self.headers, verify=False)

        status = r.status_code

        if(status == 200):
            #Successfully placed the order
            return r.json()["orderNumber"]
        else:
            raise Exception("Failed to place order")
