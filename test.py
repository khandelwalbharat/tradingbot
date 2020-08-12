from samco import SamcoOrderExecutor

a = SamcoOrderExecutor('01a626a9f7f32f94fecb06315927cad5')

status = a.place_order(tradingsymbol = 'IBULHSGFIN', transaction_type = 'BUY', order_type = 'SL', trigger_price = 240, price = 240)

print(status)
