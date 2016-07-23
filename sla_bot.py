import asyncio
import datetime as dt

import discord
from   discord.ext import commands

import SLA_bot.config as cf
from   SLA_bot.schedule import Schedule

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
    
bot.run('paste_token_here')
