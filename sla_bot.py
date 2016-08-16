import asyncio
import datetime as dt
import os
import discord
from   discord.ext import commands

from SLA_bot.config import Config as cf
from SLA_bot.schedule import Schedule

curr_dir = os.path.dirname(__file__)
configs = [
    os.path.join(curr_dir, 'docs', 'default_config.ini'),
    os.path.join(curr_dir, 'config.ini')
]
cf.load_config(configs)  

bot = commands.Bot(command_prefix='!', description='test')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    
    event_schedule = Schedule(bot)
    await event_schedule.update()
    bot.add_cog(event_schedule)
    
@bot.command()
async def test():
    await bot.say('Hello World!')


 
bot.run(cf.token)
