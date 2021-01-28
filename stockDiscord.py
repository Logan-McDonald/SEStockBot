import os,discord,asyncio,time,random
from discord.ext.commands import Bot
from discord.ext import commands
from StonkBot import Stonk

bot=commands.Bot('.')

token=''

@bot.event
async def on_ready():
    print(str(bot.user)+' has connected')

@bot.command()
async def predict(ctx,ticker):
    path=Stonk().predict(ticker)
    await ctx.send(file=discord.File(os.path.join('graphs',path+'.png')))

@bot.command()
async def train(ctx):
    Stonk().generateModel()
    await ctx.send('Model trained')

bot.run(token)