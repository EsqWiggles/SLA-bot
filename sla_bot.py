import asyncio
import datetime as dt
import os
import sys
import traceback

import discord
from   discord.ext import commands

from   SLA_bot.alertfeed import AlertFeed
from   SLA_bot.channelupdater import ChannelUpdater
from   SLA_bot.clock import Clock
from   SLA_bot.config import Config as cf
import SLA_bot.constants as cs
from   SLA_bot.pso2calendar import PSO2Calendar
import SLA_bot.util as ut





VERSION = 0.17

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


async def bot_status(bot):
    while not bot.is_closed:
        now = dt.datetime.now(dt.timezone.utc)
        try:
            time = now.astimezone(cf.tz).strftime('%H:%M %Z')
            status = '{} - {}help'.format(time, cf.cmd_prefix)
            await bot.change_presence(game=discord.Game(name=status))
        except Exception:
            print('Ignored following error:')
            print(traceback.format_exc(), file=sys.stderr)
        await asyncio.sleep(60 - now.second)
    
def strfevent(event, ref_time):
    td = '{:>7}'.format(ut.two_unit_tdelta(event.start - ref_time))
    s = event.start.astimezone(cf.tz).strftime('%b %d, %H:%M')
    e = event.end.astimezone(cf.tz).strftime('%H:%M %Z')
    return '`|{:^9}|` **{}** @ {} ~ {}'.format(td, event.name, s, e)

@bot.command()
async def find(search=''):
    if not search:
        await boy.say('Please enter a name or part of name to search.')
        return

    now = dt.datetime.now(dt.timezone.utc)   
    found = []
    for event in PSO2Calendar.events:
        if search.lower() in event.name.lower():
            found.append(event)
    if found:
        lines = []
        for name, count in PSO2Calendar.counter.items():
            if search.lower() in name.lower():
                lines.append('**{}** {}'.format(count, name))
        lines.append('')
        lines.extend([strfevent(event, now) for event in found])
        msg = '\n'.join(lines)
    else:
        msg = 'No scheduled "{}" found.'.format(search) 
    await bot.say(msg[:2000])

@bot.command(help = cs.NEXT_HELP)
async def next(search='',):
    if not PSO2Calendar.events:
        await bot.say('No scheduled events remaining.')
        return

    now = dt.datetime.now(dt.timezone.utc)          
    for event in PSO2Calendar.events:
        if event.start > now:
            next = event
            break
    
    neighbor_time = dt.timedelta(hours=1)
    if next:
        found = [next]
        later = [e for e in PSO2Calendar.events if e.start >= next.start]
        for event in later:
            if event != next and event.start - next.start <= neighbor_time:
                found.append(event)
        lines = [strfevent(event, now) for event in found]
        msg = '\n'.join(lines)
    await bot.say(msg[:2000])
        

@bot.event
async def on_ready():
    print('Logged in as: {}'.format(bot.user.name))
    print('------')
    updater = ChannelUpdater(bot)
    await updater.make_updaters()
    bot.loop.create_task(bot_status(bot))


bot.run(cf.token)


