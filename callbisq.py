import requests
import json
import sys
import pymongo
import datetime

allmarkets = 'https://markets.bisq.network/api/currencies'
btc_vnd = 'https://markets.bisq.network/api/depth?market=btc_vnd'
btc_eur = 'https://markets.bisq.network/api/depth?market=btc_eur'
currencyconverter = 'http://free.currencyconverterapi.com/api/v5/convert?q=EUR_VND&compact=y'

min_sell = 0.0
max_buy = 0.0
reference = 0.0

# buying bitcoin
resp = requests.get(btc_vnd)
if resp.status_code != 200:
    print("error")
else:
    data = json.loads(resp.text)

    min_sell = sys.float_info.max
    if 'sells' in data['btc_vnd']:
        for sell in data['btc_vnd']['sells']:
            if float(sell) < min_sell:
                min_sell = float(sell)
    else:
        print("nobody selling to VND right now")
        min_sell = 0.0

print('min_sell:', min_sell)


# selling bitcoin
resp = requests.get(btc_eur)
if resp.status_code != 200:
    print("error")
else:
    data = json.loads(resp.text)

    max_buy = 0.0
    if 'buys' in data['btc_eur']:
        for buy in data['btc_eur']['buys']:
            if float(buy) > max_buy:
                max_buy = float(buy)
    else:
        print("nobody buying with EUR right now")
        max_buy = 0.0

print('max_buy: ', max_buy)


# get reference
resp = requests.get(currencyconverter)
if resp.status_code != 200:
    print("error")
else:
    data = json.loads(resp.text)
    reference = float(data['EUR_VND']['val'])

print('reference: ', reference)


lossrate = -1000.0
if (min_sell > 0) and (max_buy > 0):
    # vnd durch eur/vnd is eur
    whatishouldget = min_sell / reference
    print('what I should get: ', whatishouldget)

    # eur - eur
    whatilose = whatishouldget - max_buy
    print('what I lose: ', whatilose)

    # in percent
    lossrate = whatilose / max_buy


print('lossrate: ', lossrate)

resultflag = 'unknown'
if lossrate > -1000.0: 
    if (lossrate < 0.02):
        if reference > 27000:
            resultflag = 'good'
        else:
            resultflag = 'exchange rate not sufficient'
    else:
        resultflag = 'bad'

print(resultflag)

DB_NAME = 'meanbase'  
DB_HOST = 'ds213688.mlab.com'
DB_PORT = 13688
DB_USER = 'maddin' 
DB_PASS = 'hAK5e2XVAw'

connection = pymongo.MongoClient(DB_HOST, DB_PORT)
db = connection[DB_NAME]
db.authenticate(DB_USER, DB_PASS)

db.converter.insert_one(
    {
        'type': 'convert',
        'vnd_btc': min_sell,
        'btc_eur': max_buy,
        'reference': reference,
        'current_time': datetime.datetime.now(),
        'lossrate': lossrate,
        'resultflag': resultflag
})