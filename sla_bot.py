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
cf.cal_path = os.path.join(curr_dir, cf.cal_path)
cf.chan_path = os.path.join(curr_dir, cf.chan_path)
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

@bot.command(pass_context=True, no_pm=True)
async def announce(ctx, filters=''):
    perm = ctx.message.channel.permissions_for(ctx.message.author)
    id = ctx.message.channel.id
    if perm.manage_channels:
        cf.set_chan(id, filters)
    
 
bot.run(cf.token)
