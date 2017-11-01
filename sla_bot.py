import asyncio
import datetime as dt
import os

import discord
from   discord.ext import commands


import SLA_bot.config as cf
curr_dir = os.path.dirname(__file__)
default_config = os.path.join(curr_dir, 'default_config.ini'),
user_config = os.path.join(curr_dir, 'config.ini')
if not os.path.isfile(user_config):
    cf.new_config(user_config)
    print("No config file found. Creating one at:\n{}".format(user_config))
    print("Please edit the config file and restart the program.")
    exit()
cf.load_configs(default_config, user_config)  


import SLA_bot.channelupdater as ChannelUpdater
import SLA_bot.constants as cs
import SLA_bot.pso2calendar as PSO2Calendar
import SLA_bot.pso2summary as PSO2Summary
import SLA_bot.util as ut




VERSION = 0.33

prefix = cf.get('General', 'command_prefix')
tzone = cf.gettimezone('General', 'timezone')
initialized = False
bot = commands.Bot(command_prefix=prefix, pm_help=True, description=cs.BOT_HELP)

async def bot_status(bot):        
    while not bot.is_closed:
        try:
            now = dt.datetime.now(dt.timezone.utc)
            time = now.astimezone(tzone).strftime('%H:%M %Z')
            status = '{} - {}help'.format(time, prefix)
            await bot.change_presence(game=discord.Game(name=status)) 
        except:
            ut.print_new_exceptions()
        now = dt.datetime.now(dt.timezone.utc)
        await asyncio.sleep(60 - now.second)

def strfevent(event, ref_time):
    s_tdelta = event.start - ref_time
    e_tdelta = event.end - ref_time
    if s_tdelta > dt.timedelta(seconds=0):
        status = ut.two_unit_tdelta(s_tdelta)
    elif e_tdelta > dt.timedelta(seconds=0):
        status = 'End ' + ut.one_unit_tdelta(e_tdelta)
    td = '{:>7}'.format(status)
    s = event.start.astimezone(tzone).strftime('%b %d, %H:%M')
    e = event.end.astimezone(tzone).strftime('%H:%M %Z')
    return '`|{:^9}|` **{}** @ {} ~ {}'.format(td, event.name, s, e)

@bot.command(help = cs.FIND_HELP)
async def find(search='', mode=''):
    now = dt.datetime.now(dt.timezone.utc) 
    search_lower = search.lower()
    found = [x for x in PSO2Calendar.events if search_lower in x.name.lower()]
    num_found = len(found)
    max = cf.getint('General', 'max_find')
    if mode != 'all':
        found = found[:max]
            
    if found:
        lines = []
        summary = PSO2Summary.count_events(PSO2Calendar.events)
        for name, count in summary.items():
            if search_lower in name.lower():
                lines.append('**{}** {}'.format(count, name))
        lines.append('')
        lines.extend([strfevent(event, now) for event in found])
        if len(found) < num_found:
            lines.append('...')
        msg = '\n'.join(lines)
    else:
        msg = 'No scheduled "{}" found.'.format(search or 'events') 
        
    if len(found) > max:
        await bot.whisper(msg[:2000])
    else:
        await bot.say(msg[:2000])

@bot.command(help = cs.NEXT_HELP)
async def next(search='',):
    now = dt.datetime.now(dt.timezone.utc)
    started = [e for e in PSO2Calendar.events if e.start <= now]
    started = [e for e in started if e.end - now <= dt.timedelta(minutes=30)]
    previous = [max(started, key=lambda e: e.end)] if started else []
    
    event_gap = dt.timedelta(minutes = 90)
    upcoming = [e for e in PSO2Calendar.events if e.start > now]
    next = [e for e in upcoming if e.start - upcoming[0].start <= event_gap]

    found = previous + next
    if found:
        lines = [strfevent(event, now) for event in found]
        msg = '\n'.join(lines)
        await bot.say(msg[:2000])
    else:
        await bot.say('No more scheduled events.')

@bot.command(pass_context=True, no_pm=True, help = cs.TOGGLE_HELP)
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
        await ChannelUpdater.load_channels()

@bot.event
async def on_ready():
    print('Logged in as: {}'.format(bot.user.name))
    print('------')
    global initialized
    if not initialized:
        await ChannelUpdater.init(bot)
        bot.loop.create_task(bot_status(bot))
        initialized = True


bot.run(cf.get('General', 'bot_token'))


