import asyncio
import datetime as dt
import math
import os
import traceback

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
    
    global event_schedule
    event_schedule = Schedule(bot)
    await event_schedule.update()
    bot.add_cog(event_schedule)
    bot.loop.create_task(make_alert())
    
@bot.command()
async def test():
    await bot.say('Hello World!')

@bot.command(pass_context=True, no_pm=True)
async def announce(ctx, filters='1,2,3,4,5,6,7,8,9,10'):
    perm = ctx.message.channel.permissions_for(ctx.message.author)
    id = ctx.message.channel.id
    if perm.manage_channels:
        cf.set_chan(id, filters)

        
# async def alertable(schedule, timeframe, last_alert):
    # now = dt.datetime.now(dt.timezone.utc)
    # latest = now + timeframe + dt.timedelta(minutes = 1)
    # upcoming = await schedule.filter_events(last_alert, latest)
    # return upcoming

def alert_text(event, ref_time):
    name = event.get('summary')
    start = event.get('dtstart').dt
    start_str = start.astimezone(cf.tz).strftime('%b %d   %H:%M %Z')
    time_left = math.ceil((start - ref_time).total_seconds() / 60)
    return '[{}min] - **{}** - {}'.format(time_left, name, start_str)
    
async def alert(id, event, first_resend, resend_time):
    channel = bot.get_channel(id)
    name = event.get('summary')
    start = event.get('dtstart').dt
    now = dt.datetime.now(dt.timezone.utc)
    resend = first_resend
    message = None

    while now < start:
        now = dt.datetime.now(dt.timezone.utc)
        alert_msg = alert_text(event, now)
        print('now: {}'.format(now))
        print('resend: {}'.format(resend))
        if now >= resend:
            try:
                await bot.delete_message(message)
                resend = resend + resend_time
                message = None
                print('deleted!')
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
            start_str = start.astimezone(cf.tz).strftime('%b %d   %H:%M %Z')
            alert_msg = '[Started] - **{}** - {}'.format(name, start_str)
            message = await bot.edit_message(message, alert_msg)
        except discord.errors.HTTPException:
            pass


async def make_alert():
    await bot.wait_until_ready()
    last_alert =  dt.datetime.now(dt.timezone.utc)
    last_alert +- dt.timedelta(hours=2)
    while not bot.is_closed:
        now = dt.datetime.now(dt.timezone.utc)
        alert_time = now + cf.alert_before
        alertable = await event_schedule.filter_events(last_alert, alert_time)

        for event in alertable:
            start = event.get('dtstart').dt
            first_resend = start
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
