import requests,json,datetime,time
import matplotlib.pyplot as plt
import numpy as np
from keras.models import Sequential
from keras.optimizers import Adam
from keras.layers import Dense
from keras.models import load_model
import math,time,random,pickle,os
join=os.path.join

class Bot:

    def __init__(self):
        self.setup()
        self.inputs=32
        self.divisor=5000

    def getEmptyModel(self):
        '''Creates a new model to train'''
        model=Sequential()
        model.add(Dense(20,activation='tanh'))
        model.add(Dense(40,activation='tanh'))
        model.add(Dense(20,activation='tanh'))
        model.add(Dense(1,activation='relu'))
        optimizer=Adam(lr=0.002)
        model.compile(loss='mean_squared_error',optimizer=optimizer,metrics=['mean_squared_error'])
        return model

    def getHistory(self,ticker):
        '''Returns the timestamps, opens, closes, highs, lows, and adjusted closes
        of a stock over the past 5 years'''
        date=datetime.datetime.today()
        day=int(date.strftime('%d'))
        date=date.strftime('%Y-%m-'+str(day))
        path=join('data',ticker,date+'.bin')
        if os.path.exists(path):
            with open(path,'rb') as file:
                data=pickle.load(file)
                return data
        url=f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
        now=datetime.datetime.now()
        now=now.replace(hour=18,minute=0,second=0)
        period2=now-datetime.timedelta(days=1)
        period1=period2-datetime.timedelta(days=180)
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
        try:
            data={
                'timestamp':[x for x in j['chart']['result'][0]['timestamp'] if x!=None],
                'open':[x for x in info['open'] if x!=None],
                'close':[x for x in info['close'] if x!=None],
                'volume':[x for x in info['volume'] if x!=None],
                'low':[x for x in info['low'] if x!=None],
                'high':[x for x in info['high'] if x!=None],
                'adjclose':[x for x in j['chart']['result'][0]['indicators']['adjclose'] if x!=None]
            }
        except:
            print(f'Invalid data for {ticker}')
            return
        if not os.path.exists(join('data',ticker)):os.mkdir(join('data',ticker))
        with open(path,'wb') as file:
            pickle.dump(data,file)
        time.sleep(1)
        return data

    def setup(self):
        folders=['data','graphs']
        for folder in folders:
            if not os.path.exists(folder):os.mkdir(folder)

    def getInputs(self,history): 
        '''Creates data to train model with'''
        hist=[]
        data=history['high']
        for x in range(self.inputs,len(data)-1):
            cur=data[x-self.inputs:x]
            answer=data[x]
            x_data=[math.sqrt(x/self.divisor) for x in cur]
            y_data=math.sqrt(answer/self.divisor)
            hist.append([x_data,y_data])
        return hist

    def testPrediction(self,model,ticker,days=50,show=False):
        history=self.getHistory(ticker)
        data=self.getInputs(history)
        x_data=np.array([np.array(x[0])for x in data])
        y_data=np.array([x[1]for x in data])
        times=history['timestamp'][-days-1:]
        real_data=history['high'][-days-1:]
        prediction_data=[real_data[0]]
        dataset=np.array([x for x in x_data[-days]])
        print(x_data[0])
        print(dataset)
        print((x**2)*self.divisor for x in dataset)
        for b in range(days):
            prediction=model.predict(dataset.reshape(-1,self.inputs))[0][0]
            next_price=(prediction**2)*self.divisor
            prediction_data.append(next_price)
            dataset=np.delete(dataset,0)
            dataset=np.append(dataset,prediction)
        plt.plot(times,real_data,color='blue',label='actual data')
        plt.plot(times[:-1],prediction_data[:-1],color='purple',label='prediction')
        plt.title(ticker)
        plt.legend()
        plt.savefig(join('data',ticker,'prediction.png'))
        plt.savefig(join('graphs',ticker+'.png'))
        if show:plt.show()
        plt.clf()

    def trainModel(self,data,model,epochs=5):
        x_data=np.array([np.array([rx for rx in x[0]])for x in data])
        y_data=np.array([x[1]for x in data])
        model.fit(x_data,y_data,epochs=epochs,shuffle=True,batch_size=32)
        model.save('trained_model')

def main():
    tickers=['TSLA','GOOGL','GME','AMC','A','AA']
    tickers=['MSFT','AAPL','AMZN','GOOG','GOOGL','FB','TCEHY','TSM','NVDA','DIS','ASML','INTC','CMCSA','ADBE','VZ','T','CSCO','NFLX','CRM','ORCL','SFTBY']
    # tickers=['GOOGL']
    # ticker='GOOGL'
    # tickers=[ticker]
    # with open('working_tickers.bin','rb') as file:
    #     tk=pickle.load(file)
    # tickers={}
    # for x in range(20):
    #     tickers[list(tk.keys())[x]]=tk[list(tk.keys())[x]]
    bot=Bot()
    alldata=[]
    for ticker in tickers:
        data=bot.getHistory(ticker)
        stuff=bot.getInputs(data)
        alldata.extend(stuff)
    model=bot.getEmptyModel()
    bot.trainModel(alldata,model,5)
    model.save('trained_model')
    model=load_model('trained_model')
    for ticker in tickers:
        bot.testPrediction(model,ticker,show=False)

if __name__=='__main__':
    main()