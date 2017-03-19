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
import SLA_bot.config as cf
import SLA_bot.constants as cs
from   SLA_bot.pso2calendar import PSO2Calendar
import SLA_bot.util as ut




VERSION = 0.17

curr_dir = os.path.dirname(__file__)
default_config = os.path.join(curr_dir, 'docs', 'default_config.ini'),
user_config = os.path.join(curr_dir, 'config.ini')
cf.load_configs(default_config, user_config)  

prefix = cf.get('General', 'command_prefix')
tzone = cf.gettimezone('General', 'timezone')

bot = commands.Bot(command_prefix=prefix, pm_help = True, description=cs.BOT_HELP)

initialized = False

                   
async def bot_status(bot):
    while not bot.is_closed:
        now = dt.datetime.now(dt.timezone.utc)
        try:
            time = now.astimezone(tzone).strftime('%H:%M %Z')
            status = '{} - {}help'.format(time, prefix)
            await bot.change_presence(game=discord.Game(name=status))
        except Exception:
            print('Ignored following error:')
            print(traceback.format_exc(), file=sys.stderr)
        await asyncio.sleep(60 - now.second)
    
def strfevent(event, ref_time):
    td = '{:>7}'.format(ut.two_unit_tdelta(event.start - ref_time))
    s = event.start.astimezone(tzone).strftime('%b %d, %H:%M')
    e = event.end.astimezone(tzone).strftime('%H:%M %Z')
    return '`|{:^9}|` **{}** @ {} ~ {}'.format(td, event.name, s, e)

@bot.command()
async def find(search='', mode=''):
    if not search:
        await boy.say('Please enter a name or part of name to search.')
        return

    now = dt.datetime.now(dt.timezone.utc)   
    found = []
    for event in PSO2Calendar.events:
        if search.lower() in event.name.lower():
            found.append(event)
            
    max = cf.getint('General', 'max_find')
    if mode != 'all':
        found = found[:max]
            
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
        
    if len(found) > max:
        await bot.whisper(msg[:2000])
    else:
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
        
@bot.command(pass_context=True, no_pm=True)
async def toggle(ctx):
    perm = ctx.message.channel.permissions_for(ctx.message.author)
    if perm.manage_channels:
        id = ctx.message.channel.id
        cf.reload()
        if id in cf.channels():
            cf.remove_option('Channels', id)
        else:
            cf.set('Channels', id, '')
        cf.save()
        await updater.load_channels()

@bot.event
async def on_ready():
    print('Logged in as: {}'.format(bot.user.name))
    print('------')
    global initialized
    if not initialized:
        global updater
        updater = ChannelUpdater(bot)
        await updater.make_updaters()
        bot.loop.create_task(bot_status(bot))
        initialized = True


bot.run(cf.get('General', 'bot_token'))


