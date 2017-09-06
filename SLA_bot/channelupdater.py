import asyncio
import datetime as dt

import discord

import SLA_bot.alertfeed as AlertFeed
import SLA_bot.clock as Clock
import SLA_bot.config as cf
import SLA_bot.pso2calendar as PSO2Calendar
import SLA_bot.pso2escalendar as PSO2esCalendar
import SLA_bot.util as ut

bot = None
channel_messages = {}
modules = []

async def init(discord_bot):
    global bot
    global modules
    bot = discord_bot
    modules = [
        (Clock.fetch, cf.getint('Clock', 'update_interval')),
        (AlertFeed.fetch, cf.getint('PSO2 Feed', 'update_interval')),
        (PSO2Calendar.fetch, cf.getint('PSO2 Calendar', 'update_interval')),
        (PSO2esCalendar.fetch, cf.getint('PSO2es Calendar', 'update_interval')),
    ]
    await make_updaters()

async def recycle_messages(channel):
    try:
        messages = bot.logs_from(channel, 100, reverse=True)
        recycled = []
        async for msg in messages:
            if msg.author.id == bot.user.id:
                recycled.append(msg)
            else:
                recycled = []
            if len(recycled) >= len(modules):
                break
        return recycled
    except (discord.errors.Forbidden, discord.errors.NotFound):
        return []

async def write_content(channel, nth_msg, content):
    global channel_messages
    m = channel_messages[channel]
    c = content[:2000]
    try:
        m[nth_msg] = await bot.edit_message(m[nth_msg], c)
    except IndexError:
        try:
            m.append( await bot.send_message(channel, c) )
            channel_messages[channel] = await recycle_messages(channel)
        except (discord.errors.Forbidden, discord.errors.NotFound):
            pass
    except discord.errors.NotFound:
        del m[nth_msg]
    
async def updater(contentFunc, nth_msg, interval):
    while not bot.is_closed:
        try:
            content = await contentFunc()
            for channel in channel_messages:
                await write_content(channel, nth_msg, content)
        except:
            ut.print_new_exceptions()
        await asyncio.sleep(interval)
        
async def load_channels():
    global channel_messages
    channel_messages = {}
    for c in cf.channels():
        chan = bot.get_channel(c)
        channel_messages[chan] = await recycle_messages(chan)
        
async def make_updaters():
    await load_channels()
    for i, m in enumerate(modules):
        bot.loop.create_task(updater(m[0], i, m[1]))
