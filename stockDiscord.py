import os,discord,asyncio,time,random,pickle,requests
from discord.ext.commands import Bot
from discord.ext import commands
from StonkBot import Stonk

bot=commands.Bot('.')

token='ODA0NDMwMzM1NzQ3Njg2NDc1.YBMOIQ.PWckD-jrrrUJgarmBoovXEcHiH8'

@bot.event
async def on_ready():
    print(str(bot.user)+' has connected')

@bot.command()
async def predict(ctx,ticker,days=100):
    if int(days)<1 or int(days)>365:
        await ctx.send('Valid numbers are between 0 and 366')
        return
    path=Stonk().predict(ticker,int(days))
    await ctx.send(file=discord.File(os.path.join('graphs',path+'.png')))

@bot.command()
async def train(ctx):
    Stonk().generateModel()
    await ctx.send('Model trained')

@bot.command()
async def tickers(ctx):
    tickers=Stonk().getTickers()
    ticks=sorted(tickers.keys(),key=lambda x:x.lower())
    st=''
    for i,s in enumerate(ticks):
        st+=f'{i+1}. {s} - {tickers[s]}\n'
    await ctx.send(st)

@bot.command()
async def add(ctx,*args):
    st,re=Stonk().addTicker(' '.join(args))
    await ctx.send(re)

@bot.command()
async def remove(ctx,*args):
    st,re=Stonk().removeTicker(' '.join(args))
    await ctx.send(re)

bot.run(token)