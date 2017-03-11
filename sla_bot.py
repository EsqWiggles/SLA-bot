import asyncio
import collections
import datetime as dt
import math
import os
import sys
import traceback

import discord
from   discord.ext import commands
import pytz

from   SLA_bot.alertsystem import AlertSystem
from   SLA_bot.config import Config as cf
import SLA_bot.constants as cs
from   SLA_bot.schedule import Schedule
import SLA_bot.util as ut
from   SLA_bot.alertfeed import AlertFeed
from   SLA_bot.clock import Clock
from   SLA_bot.channelupdater import ChannelUpdater
from   SLA_bot.pso2calendar import PSO2Calendar

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

# event_schedule = Schedule(bot)
# bot.add_cog(event_schedule)

# async def update_schedule():
    # while not bot.is_closed:
        # try:
            # await event_schedule.update()
        # except Exception:
            # print('Ignored following error:')
            # print(traceback.format_exc(), file=sys.stderr)
        # await asyncio.sleep(cf.refresh_time)

# bot.loop.create_task(update_schedule())

# def country_zone():
    # original = pytz.country_timezones
    # inverted = {}
    # for k, v in original.items():
        # for zone in v:
            # inverted[zone] = pytz.country_names[k]
    # return inverted
    
# async def clock(bot):
    # while not bot.is_closed:
        # now = dt.datetime.now(dt.timezone.utc)
        # try:
            # time = now.astimezone(cf.tz).strftime('%H:%M %Z')
            # help = 'Type {}help'.format(cf.cmd_prefix)
            # status = '{} - {}'.format(time, help)
            # await bot.change_status(game=discord.Game(name=status))
        # except Exception:
            # print('Ignored following error:')
            # print(traceback.format_exc(), file=sys.stderr)
        # await asyncio.sleep(60 - now.second)

# @bot.command(help = cs.TZLIST_HELP)
# async def tzlist(mode='other'):
    # countries = collections.OrderedDict()
    # others = collections.OrderedDict()
    # country_codes = {x.lower() for x in pytz.country_timezones.keys()} 
    # cc_from_tz = country_zone()
    # for k, v in cf.custom_tz.items():
        # if k in country_codes:
            # countries[k] = v
        # else:
            # others[k] = v

    # if mode == 'other':
        # selected = others
    # elif mode == 'country':
        # selected = countries
    # else:
        # selected = collections.OrderedDict()

    # lines = []
    # for k, v in selected.items():
        # country = cc_from_tz[v] if v in cc_from_tz else 'No Country'
        # line = '{} = {} - {}'.format(k, v, country)
        # lines.append(line)
    # msg = ut.chunk_string('\n'.join(lines), cs.MSG_CHAR_LIMIT)
    # await ut.quiet_say(bot, msg, cf.max_line)

# @bot.command(help = cs.TZINFO_HELP)
# async def tzinfo(timezone=''):
    # tz = ut.parse_tz(timezone, cf.tz, cf.custom_tz)
    
    # country = 'No Country'
    # area = getattr(tz, 'zone', 'Custom time zone')
    # if hasattr(tz, 'zone'):
        # for k, v in pytz.country_timezones.items():
            # if tz.zone in v:
                # country = pytz.country_names[k]
                # break
    
    # dt_line = dt.datetime.now(tz).strftime('%a %b %m, %H:%M %Z (UTC%z)')
    # msg = '{} = {} - {}\n{}'.format(timezone, area, country, dt_line)
    
    # await ut.quiet_say(bot, msg, cf.max_line)

    
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


bot.run(cf.token)


