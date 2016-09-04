import asyncio
import datetime as dt
import math
import os
import traceback

import discord
from   discord.ext import commands

from   SLA_bot.config import Config as cf
import SLA_bot.constants as cs
from   SLA_bot.schedule import Schedule

VERSION = 0.10

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

@bot.event
async def on_ready():
    print('Logged in as: {}'.format(bot.user.name))
    print('------')
    #bot.loop.create_task(make_alert())

@bot.command(pass_context=True, no_pm=True)
async def announce(ctx, filters='1,2,3,4,5,6,7,8,9,10'):
    perm = ctx.message.channel.permissions_for(ctx.message.author)
    id = ctx.message.channel.id
    if perm.manage_channels:
        cf.set_chan(id, filters)


def alert_text(event, ref_time):
    time_left = math.ceil((event.start - ref_time).total_seconds() / 60)
    return '[{}min] - {}'.format(time_left, event.duration(cf.tz))
    
async def alert(id, event, first_resend, resend_time):
    channel = bot.get_channel(id)
    now = dt.datetime.now(dt.timezone.utc)
    resend = first_resend
    message = None

    while now < event.start:
        now = dt.datetime.now(dt.timezone.utc)
        alert_msg = alert_text(event, now)
        if now >= resend:
            try:
                await bot.delete_message(message)
                resend = resend + resend_time
                message = None
            except discord.errors.HTTPException:
                continue
        if message == None:
            try:
                message = await bot.send_message(channel, alert_msg)
            except (discord.errors.HTTPException, discord.errors.Forbidden):
                continue
            except (discord.errors.NotFound, discord.errors.InvalidArgument):
                break
        else:
            try:
                message = await bot.edit_message(message, alert_msg)
            #not found should break
            except discord.errors.HTTPException:
                continue
        await asyncio.sleep(60)
    if message != None:
        try:
            alert_msg = '[Started] - {}'.format(event.duration(cf.tz))
            message = await bot.edit_message(message, alert_msg)
        except discord.errors.HTTPException:
            pass


async def make_alert():
    await bot.wait_until_ready()
    last_alert =  dt.datetime.now(dt.timezone.utc)
    while not bot.is_closed:
        now = dt.datetime.now(dt.timezone.utc)
        alert_time = now + cf.alert_before
        alertable = event_schedule.from_range(last_alert, alert_time)
        for event in alertable:
            first_resend = event.start
            while first_resend > now:
                first_resend -= cf.alert_every
            first_resend += cf.alert_every
            for chan in cf.channels:
                bot.loop.create_task(alert(chan[0], event, first_resend,
                                           cf.alert_every))
        if len(alertable) > 0:
            last_alert = alert_time
        await asyncio.sleep(60)


        
bot.run(cf.token)


