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
        self.inputs=24
        self.divisor=10000

    def getEmptyModel(self):
        '''Creates a new model to train'''
        model=Sequential()
        model.add(Dense(20,activation='tanh'))
        model.add(Dense(1,activation='tanh'))
        optimizer=Adam(lr=0.001)
        model.compile(loss='mean_squared_error',optimizer=optimizer,metrics=['mean_squared_error'])
        return model

    def getHistory(self,ticker):
        '''Returns the timestamps, opens, closes, highs, lows, and adjusted closes
        of a stock over the past 5 years'''
        date=datetime.datetime.today()
        date=date.replace(day=18)
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

    def getInputs(self,history): 
        '''Creates data to train model with'''
        hist=[]
        data=history['high']
        for x in range(self.inputs,len(data)-1):
            cur=data[x-self.inputs:x]
            f1=data[x]
            f2=cur[-1]
            a=((f1-f2)/f2)
            b=(history['timestamp'][x+1]-history['timestamp'][x])/(3600*24)
            answer=a/b
            hist.append([cur,answer])
        return hist

    def trainModel(self,data,model,epochs=5):
        x_data=np.array([np.array([rx/self.divisor for rx in x[0]])for x in data])
        y_data=np.array([x[1]for x in data])
        model.fit(x_data,y_data,epochs=epochs,shuffle=True,batch_size=32)
        model.save('trained_model')

    def test(self,model):
        h=self.getHistory('TSLA')
        inp=self.getInputs(h)
        x_data=np.array([np.array(x[0]) for x in inp])
        y_data=np.array([x[1] for x in inp])
        model.fit(x_data,y_data,epochs=3,shuffle=True)
        last=h['high'][-100:]
        times=h['timestamp'][-100:]
        plt.plot(times,last)
        pm=x_data[-101]
        preds=[]
        for _ in range(100):
            pr=model.predict(pm.reshape(-1,self.inputs))
            nx=pm[-1]*(1+pr[0][0])
            preds.append(nx)
            pm[0]=pm[-1]
            pm[-1]=nx
        plt.plot(times,preds)
        plt.show()

    def testPrediction(self,model,ticker,days=100,show=False):
        history=self.getHistory(ticker)
        data=self.getInputs(history)
        x_data=np.array([np.array(x[0])for x in data])
        y_data=np.array([x[1]for x in data])
        times=history['timestamp'][-days:]
        real_data=history['high'][-days:]
        prediction_data=[]
        dataset=x_data[(-days)-1]
        # dataset=np.array([x/self.divisor for x in dataset])
        
        for b in range(days):
            dataset=np.array([x/self.divisor for x in dataset])
            #prediction=model.predict(dataset.reshape(-1,self.inputs))[0][0]
            prediction=model.predict(dataset.reshape(-1,self.inputs))[0][0]
            next_price=dataset[-1]*(1+prediction)
            prediction_data.append(next_price*self.divisor)
            dataset=x_data[((-days)+2)+b]
            # dataset=np.delete(dataset,0)
            # dataset=np.append(dataset,next_price)
        plt.plot(times,real_data,color='blue')
        plt.plot(times[:-1],prediction_data[:-1],color='purple')
        plt.title(ticker)
        plt.savefig(join('data',ticker,'prediction.png'))
        plt.savefig(join('graphs',ticker+'.png'))
        if show:plt.show()
        plt.clf()

    def getData(self):
        with open('working_tickers.bin','rb') as file:
            tickers=pickle.load(file)
        data=[]
        for tick in tickers:
            history=self.getHistory(tick)
            data.extend(self.getInputs(history))
        return data

    def setup(self):
        folders=['data','graphs']
        for folder in folders:
            if not os.path.exists(folder):os.mkdir(folder)
        tickers={
            # 'TSLA':'Tesla',
            # 'GOOGL':'Google',
            'AAPL':'Apple'
        }
        for tick in tickers:
            path=join('data',tick)
            if not os.path.exists(path):
                os.mkdir(path)
        with open('tickers.bin','wb') as file:
            pickle.dump(tickers,file)

    def readTickers(self):
        with open('tickers.txt','r') as file:
            lines=file.readlines()
        tickers={}
        for l in range(len(lines)):
            line=lines[l]
            tk=line[:line.find(' ')]
            name=line[line.find('-')+2:line.find('\n')]
            tickers[tk]=name
        return tickers

    def filterTickers(self):
        tickers=self.readTickers()
        working={}
        s=1
        total=len(tickers)
        for tick in tickers:
            print(f'{s}/{total}')
            s+=1
            data=self.getHistory(tick)
            if data:
                if len(data['timestamp'])<128:continue
                working[tick]=tickers[tick]
            time.sleep(1)
        with open('working_tickers.bin','wb') as file:
            pickle.dump(working,file)
    
    def printTickers(self):
        with open('working_tickers.bin','rb') as file:
            tickers=pickle.load(file)
        print(len(tickers))
    
    def generateGraphs(self):
        model=load_model('trained_model')
        with open('working_tickers.bin','rb') as file:
            tickers=pickle.load(file)
        for x in range(len(tickers)):
            try:
                self.testPrediction(model,list(tickers.keys())[x])
            except Exception as e:
                print(e)

    def cycle(self):
        model=self.getEmptyModel()
        data=self.getData()
        self.trainModel(data,model,3)
        self.generateGraphs()


def main():
    bot=Bot()
    bot.cycle()
    #model=load_model('trained_model')

if __name__=='__main__':
    main()