import requests
headers = {
  'Accept': 'application/json',
  'x-session-token': '0d05294673bc035538ce9fc4a79434bd'
}

r = requests.get('https://api.stocknote.com/intraday/candleData', params={
  'symbolName': 'INFY900PE',  'exchange':'NFO', 'fromDate': '2020-08-01 09:00:00'
}, headers = headers)

print(r.json())
