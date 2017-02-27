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
channel_messages = {}
                   
class Cabinet:
    module_cache = collections.OrderedDict()
    module_cache[Clock] = 'No data'
    module_cache[AlertFeed] = 'No data'

    async def update():
        for m in Cabinet.module_cache:
            Cabinet.module_cache[m] = await m.fetch()
            
    def contents():
        components = []
        for k, v in Cabinet.module_cache.items():
            components.append(v)
        return components
            

async def recyle_messages(channel):
    required_messages = len(Cabinet.module_cache)
    messages = bot.logs_from(channel, limit=required_messages)
    recyled = []
    async for msg in messages:
        if msg.author.id == bot.user.id:
            recyled.append(msg)
        else:
            break
    return recyled
            
async def write(chan_msgs):
    texts = Cabinet.contents()
    required_messages = len(Cabinet.module_cache)
    for chan, msgs in chan_msgs.items():
        if chan == None:
            continue
            
        for i in range(required_messages):
            try:
                msgs[i] = await bot.edit_message(msgs[i], texts[i])
            except IndexError:
                new_msg = await bot.send_message(chan, texts[i])
                msgs.append(new_msg)
            except discord.errors.NotFound:
                chan_msgs[chan] = await recyle_messages(chan)
                break
        
async def updater():
    while not bot.is_closed:
        try:
            await Cabinet.update()
            await write(channel_messages)
        except Exception:
            print('Ignored following error:')
            print(traceback.format_exc(), file=sys.stderr)

        await asyncio.sleep(20)



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
    
@bot.event
async def on_ready():
    print('Logged in as: {}'.format(bot.user.name))
    print('------')
    # alerter = AlertSystem(bot, event_schedule)
    # bot.add_cog(alerter)
    # bot.loop.create_task(alerter.feed_update())
    # bot.loop.create_task(alerter.update())
    # bot.loop.create_task(clock(bot))
    for c in cf.channels:
        channel = bot.get_channel(c[0])
        channel_messages[channel] = await recyle_messages(channel)

    
    bot.loop.create_task(updater())

bot.run(cf.token)


