import requests,datetime,json

def main():
    data=getHistory('TSLA')
    for key in data: # Shows first 5 items in each list to show it works
        print(f'{key}: {data[key][:5]}')

def getHistory(ticker):
    '''Returns the timestamps, opens, closes, highs, lows, and adjusted closes of a specified stock over the past 5 years'''
    url=f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
    now=datetime.datetime.now()
    now=now.replace(hour=18,minute=0,second=0)
    period2=now-datetime.timedelta(days=1)
    period1=period2-datetime.timedelta(days=365*5)
    period1,period2=str(int(period1.timestamp())),str(int(period2.timestamp()))
    headers={
        'authority': 'query1.finance.yahoo.com',
        'method': 'GET',
        'path': f'/v8/finance/chart/{ticker}',
        'scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'origin': 'https://finance.yahoo.com',
        'pragma': 'no-cache',
        'referer': f'https://finance.yahoo.com/quote/{ticker}/history',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
    }
    params={
        'formatted':'true',
        'region':'US',
        'includeAdjustedClose':'true',
        'interval':'1d',
        'period1':str(period1),
        'period2':str(period2),
        'events':'div|split',
        'useYfid':'true',
        'corsDomain':'finance.yahoo.com'
    }
    r=requests.get(url,headers=headers,params=params)
    if r.status_code!=200:
        print(f'failed to get ticker {ticker}')
        return
    j=json.loads(r.text)
    info=j['chart']['result'][0]['indicators']['quote'][0]
    data={
        'timestamp':[x for x in j['chart']['result'][0]['timestamp'] if x!=None],
        'open':[x for x in info['open'] if x!=None],
        'close':[x for x in info['close'] if x!=None],
        'volume':[x for x in info['volume'] if x!=None],
        'low':[x for x in info['low'] if x!=None],
        'high':[x for x in info['high'] if x!=None],
        'adjclose':[x for x in j['chart']['result'][0]['indicators']['adjclose'][0]['adjclose'] if x!=None]
    }
    return data

if __name__=='__main__':
    main()