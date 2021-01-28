import requests,json,datetime,time
import matplotlib.pyplot as plt
import numpy as np
from keras.models import Sequential
from keras.optimizers import Adam
from keras.layers import Dense
from keras.models import load_model
import math,time,random,pickle,os

class Stonk:

    def __init__(self):
        '''Initialize the stock bot and model if it exists'''
        self.setup()
        self.inputs=32
        self.filename='stock_model'
        self.model=None
        if os.path.exists('stock_model'):self.model=load_model('stock_model')

    def getHistory(self,ticker):
        '''Returns the timestamps, opens, closes, highs, lows, and adjusted closes
        of a stock over the past 5 years'''
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
            'adjclose':[x for x in j['chart']['result'][0]['indicators']['adjclose'] if x!=None]
        }
        date=datetime.datetime.now().strftime("%m-%d-%y")
        with open(os.path.join('data',ticker,'history',f'{ticker}_{date}.bin'),'wb') as file:
            pickle.dump(data,file)
        return data

    def getEmptyModel(self):
        '''Creates a new model to train'''
        model=Sequential()
        model.add(Dense(20,input_shape=((self.inputs,)),activation='relu'))
        model.add(Dense(30))
        model.add(Dense(1,activation='tanh'))
        model.compile(loss='mean_squared_error',optimizer='adam',metrics=['mean_squared_error'])
        return model

    def generateModel(self):
        '''Creates, trains, and returns a model'''
        data=self.getTrainingData()
        model=self.getEmptyModel()
        self.model=self.trainModel(data,model)

    def getTrainingData(self):
        '''Returns list of training sets'''
        with open(os.path.join('data','tickers.bin'),'rb') as file:
            tickers=pickle.load(file)
        data=[]
        for tick in tickers:
            print(tick)
            if os.listdir(os.path.join('data',tick,'history')):
                with open(os.path.join('data',tick,'history',os.listdir(os.path.join('data',tick,'history'))[0]),'rb') as file:
                    data.extend(self.getInputs(pickle.load(file)))
                    continue
            data.extend(self.getInputs(self.getHistory(tick)))
        return data

    def getInputs(self,history):
        '''Creates data to train model with'''
        hist=[]
        if len(history['high'])<self.inputs:return
        data=[x/1000 for x in history['high']]
        for x in range(self.inputs,len(data)-1):
            cur=data[x-self.inputs:x]
            f1=data[x]
            f2=cur[-1]
            a=((f1-f2)/f2)
            b=(history['timestamp'][x+1]-history['timestamp'][x])/(3600*24)
            answer=a/b
            hist.append([cur,answer])
        return hist

    def predict(self,ticker,days=100):
        '''Uses the trained model to predict the price of a stock for the next [days] days'''
        date=datetime.datetime.now().strftime("%m-%d-%y")
        try:
            with open(os.path.join('data',ticker,'history',f'{ticker}_{date}.bin'),'rb') as file:
                data=pickle.load(file)
        except FileNotFoundError:
            os.mkdir(os.path.join('data',ticker))
            os.mkdir(os.path.join('data',ticker,'history'))
            os.mkdir(os.path.join('data',ticker,'predictions'))
            os.mkdir(os.path.join('data',ticker,'predictions','graphs'))
            os.mkdir(os.path.join('data',ticker,'predictions','data'))
            data=self.getHistory(ticker)
        dataset=np.array([np.array([i[0] for i in self.getInputs(data)]).reshape(-1,self.inputs)[-1]])
        predictions=[]
        for x in range(days):
            guess=self.model.predict(dataset)
            new_price=((1000*dataset[0][-1])*(1+guess[0][0]))
            predictions.append(new_price)
            dataset=np.delete(dataset,0)
            dataset=np.array([np.append(dataset,new_price/1000)])
        with open(os.path.join('data',ticker,'predictions','data',f'{ticker}_{days}_{date}.bin'),'wb') as file:
            pickle.dump(predictions,file)
        old_days=data['timestamp'][-100:]
        old_days=[(x-datetime.datetime.now().timestamp())/(3600*24) for x in old_days]
        old_prices=data['high'][-100:]

        plt.plot(old_days,old_prices,label='Past')
        new_days=range(days+1)
        predictions.insert(0,old_prices[-1])
        plt.plot(new_days,predictions,label='Predictions')
        plt.legend()
        plt.xlabel('Time (Days)')
        plt.ylabel('Price ($)')
        plt.title(f'{ticker} - {date}')
        name=f'{ticker}_{days}_{date}'
        plt.savefig(os.path.join('data',ticker,'predictions','graphs',name))
        plt.savefig(os.path.join('graphs',name))
        plt.clf()
        return name
    
    def trainModel(self,data,model):
        '''Trains model using given data'''
        x_data=np.array([i[0] for i in data]).reshape(-1,self.inputs)
        y_data=np.array([i[1] for i in data]).reshape(-1,1)
        model.fit(x_data,y_data,epochs=10,shuffle=True)
        model.save(self.filename)
        return model    

    def generateGraphs(self):
        '''Generates graph for stocks currently being tracked'''
        with open(os.path.join('data','tickers.bin'),'rb') as file:
            tickers=pickle.load(file)
        for tick in tickers:
            self.predict(tick)

    def setup(self):
        if not os.path.exists('data'):os.mkdir('data')
        if not os.path.exists('graphs'):os.mkdir('graphs')
        tickers={
            'TSLA':'Tesla',
            'GME':'Gamestop',
            'BTC-USD':'Bitcoin',
            'NOK':'Nokia Corporation',
            'AAL':'American Airlines Group Inc.',
            'BB':'BlackBerry Limited',
            'AAPL':'Apple Inc.',
            'PLTR':'Palantir Technologies Inc.',
            'GOOGLE':'Google',
            'AMZN':'Amazon.com, Inc.'
        }
        with open(os.path.join('data','tickers.bin'),'wb') as file:
            pickle.dump(tickers,file)
        for tick in tickers:
            if not os.path.exists(os.path.join('data',tick)):
                os.mkdir(os.path.join('data',tick))
                os.mkdir(os.path.join('data',tick,'predictions'))
                os.mkdir(os.path.join('data',tick,'predictions','graphs'))
                os.mkdir(os.path.join('data',tick,'predictions','data'))
                os.mkdir(os.path.join('data',tick,'history'))

def main():
    chubs=Stonk()
    chubs.generateModel()
    chubs.generateGraphs()

if __name__=='__main__':
    main()
