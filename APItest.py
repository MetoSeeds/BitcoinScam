import requests
from datetime import date
from time import mktime


start = date(2017, 12, 20)
end = date.today()
period = 14400
currencyPair = 'USDT_BTC'
command = 'returnChartData'

start = mktime(start.timetuple())
end = mktime(end.timetuple())

start = int(start)
end = int(end)
start = str(start)
end = str(end)
period = str(period)

url = 'https://poloniex.com/public?command='+ command +'&currencyPair='+ currencyPair +'&start='+ start + '&end=' + end + '&period=' + period

r = requests.get(url)
json_string = r.json()
print (json_string)
