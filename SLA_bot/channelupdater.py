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

async def init(discord_bot):
    global bot
    bot = discord_bot
    await make_updaters()

async def recycle_messages(channel):
    try:
        messages = bot.logs_from(channel, 100)
        async for msg in messages:
            if msg.author.id == bot.user.id and msg.embeds:
                return msg
    except (discord.errors.Forbidden, discord.errors.NotFound):
        return None
    return None

async def write_content(channel, content, embed):
    global channel_messages
    message = channel_messages[channel]
    try:
        if message == None:
            channel_messages[channel] = await bot.send_message(channel, content, embed=embed)
        else: 
            channel_messages[channel] = await bot.edit_message(message, content, embed=embed)
    except discord.errors.NotFound: 
        channel_messages[channel] = None
    except discord.errors.Forbidden:
        pass

async def build_message():
    content = None
    embed=discord.Embed(title=Clock.read(), description='** **',  color=0x3e9eff)
    alert_header, alert_body = AlertFeed.read().split('\n', maxsplit=1)
    if AlertFeed.is_unscheduled():
        embed.add_field(name=alert_header, value=alert_body, inline=True)
    embed.add_field(name='**PSO2 Schedule**', value=PSO2Calendar.read(), inline=True)
    embed.add_field(name='**PSO2es**', value=PSO2esCalendar.read(), inline=True)
    if not AlertFeed.is_unscheduled():
        embed.add_field(name=alert_header, value=alert_body, inline=True)
    return (content, embed)

        
async def update_messages(interval):
    while not bot.is_closed:
        try:
            Clock.update()
            content, embed = await build_message()
            for channel, messages in channel_messages.items():
                await write_content(channel, content, embed)
        except asyncio.CancelledError:
            break
        except:
            ut.print_new_exceptions()
        await asyncio.sleep(interval)
    
async def load_channels():
    global channel_messages
    channel_messages = {}
    for c in cf.channels():
        chan = bot.get_channel(c)
        channel_messages[chan] = await recycle_messages(chan)

async def updater(updateFunc, interval):
    while not bot.is_closed:
        try:
            await updateFunc()
        except asyncio.CancelledError:
            break
        except:
            ut.print_new_exceptions()
        await asyncio.sleep(interval)
        
async def make_updaters():
    await load_channels()
    update_delays = {
        AlertFeed.update : cf.getint('PSO2 Feed', 'update_interval'),
        PSO2Calendar.update : cf.getint('PSO2 Calendar', 'update_interval'),
        PSO2esCalendar.update : cf.getint('PSO2es Calendar', 'update_interval')}
    for func, delay in update_delays.items():
        bot.loop.create_task(updater(func, delay))
    bot.loop.create_task(update_messages(cf.getint('General', 'channel_update_interval')))
