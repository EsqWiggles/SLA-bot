import asyncio
import datetime as dt
import math
import os
import traceback

import discord
from   discord.ext import commands

from   SLA_bot.config import Config as cf
import SLA_bot.constants as cs
from   SLA_bot.alertsystem import AlertSystem
from   SLA_bot.schedule import Schedule

VERSION = 0.15

curr_dir = os.path.dirname(__file__)
configs = [
    os.path.join(curr_dir, 'docs', 'default_config.ini'),
    os.path.join(curr_dir, 'config.ini')
]
cf.cal_path = os.path.join(curr_dir, cf.cal_path)
cf.chan_path = os.path.join(curr_dir, cf.chan_path)
cf.load_config(configs)  




bot = commands.Bot(command_prefix=cf.cmd_prefix, pm_help = True,
                   description=cs.BOT_HELP)
event_schedule = Schedule(bot)
bot.add_cog(event_schedule)

async def update_schedule():
    while not bot.is_closed:
        await event_schedule.update()
        await asyncio.sleep(cf.refresh_time)
        
bot.loop.create_task(update_schedule())

async def clock(bot):
    while not bot.is_closed:
        now = dt.datetime.now(dt.timezone.utc)
        time = now.astimezone(cf.tz).strftime('%H:%M %Z')
        help = 'Type {}help'.format(cf.cmd_prefix)
        status = '{} - {}'.format(time, help)
        await bot.change_status(game=discord.Game(name=status))
        await asyncio.sleep(60 - now.second)

@bot.event
async def on_ready():
    print('Logged in as: {}'.format(bot.user.name))
    print('------')
    alerter = AlertSystem(bot, event_schedule)
    bot.add_cog(alerter)
    bot.loop.create_task(alerter.feed_update())
    bot.loop.create_task(alerter.update())
    bot.loop.create_task(clock(bot))


    
bot.run(cf.token)


