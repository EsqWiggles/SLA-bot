"""Update modules and channel messages.

Manage the update of modules and compile their text into one big message to
send to the configured Discord channels.
"""

import aiohttp
import asyncio
import datetime as dt

import discord

import SLA_bot.config as cf
import SLA_bot.util as ut
import SLA_bot.module.alertfeed as AlertFeed
import SLA_bot.module.bumpedrss as bumpedRSS
import SLA_bot.module.clock as Clock
import SLA_bot.module.pso2calendar as PSO2Calendar
import SLA_bot.module.pso2escalendar as PSO2esCal
import SLA_bot.module.pso2rss as PSO2RSS
import SLA_bot.module.pso2summary as PSO2Summary


bot = None
channel_messages = {}
color = int(cf.get('General', 'embed_color'), 16)

async def init(discord_bot):
    """Load module updaters onto the bot loop. Call once."""
    global bot
    bot = discord_bot
    await make_updaters()
        
async def make_updaters():
    """Create and load the module and channel updaters into the bot loop."""
    await load_channels()
    update_delays = {
        AlertFeed.update : cf.getint('PSO2 Feed', 'update_interval'),
        bumpedRSS.update : cf.getint('bumped RSS', 'update_interval'),
        PSO2Calendar.update : cf.getint('PSO2 Calendar', 'update_interval'),
        PSO2esCal.update : cf.getint('PSO2es Calendar', 'update_interval'),
        PSO2RSS.update : cf.getint('PSO2 RSS', 'update_interval'),
        update_messages : cf.getint('General', 'channel_update_interval')}
    for func, delay in update_delays.items():
        bot.loop.create_task(updater(func, delay))

async def load_channels():
    """Load the channel IDs from config."""
    global channel_messages
    channel_messages = {}
    for c in cf.channels():
        chan = bot.get_channel(int(c))
        channel_messages[chan] = await recycle_messages(chan)

async def recycle_messages(channel):
    """Return the last message sent by this bot in the channel.
    
    Only searches the last 100 messages in the channel.
    
    Args:
        channel (str): ID of the channel to search in.
    
    Returns:
        A Message object of the last message sent by this bot or None.
    """
    try:
        async for msg in channel.history(limit=100):
            if msg.author.id == bot.user.id and msg.embeds:
                return msg
    except (discord.errors.Forbidden, discord.errors.NotFound):
        return None
    return None

async def update_messages():
    """Build a new message and send it to all the channels."""
    #Clock does not use external source so just update every message
    Clock.update()
    content, embed = await build_message()
    ignored_errors = {}
    for channel, messages in channel_messages.items():
        try:
            await write_content(channel, content, embed)
        except ut.ConnectionErrors + (IndexError,) as e:
            ignored_errors[type(e).__name__] = e
        except discord.errors.HTTPException as e:
            ignored_errors['HTTP error'] = e

    if ignored_errors:
        lines = ['Failed connection to Discord:']
        for name, msg in ignored_errors.items():
            lines.append('  {}: {}'.format(name, msg))
        ut.note('\n'.join(lines))
        
async def updater(updateFunc, interval):
    """Create an update loop to call updateFunc every interval seconds."""
    while not bot.is_closed():
        try:
            await updateFunc()
        except asyncio.CancelledError:
            break
        except Exception:
            ut.print_new_exceptions()
        await asyncio.sleep(interval)

async def build_message():
    """Return the compiled text of the modules as a content and embed tuple."""
    content = ' ' #clear any body text
    embed=discord.Embed(title=Clock.read(), description='** **',  color=color)
    alert_header, alert_body = AlertFeed.read().split('\n', maxsplit=1)
    if AlertFeed.is_unscheduled():
        embed.add_field(name=alert_header, value=alert_body, inline=False)
    if PSO2Calendar.events:
        embed.add_field(name='**PSO2 Schedule**', value=PSO2Calendar.read())
        embed.add_field(name='**PSO2 Summary**', value=PSO2Summary.read())
    if PSO2esCal.events:
        embed.add_field(name='**PSO2es**', value=PSO2esCal.read(), inline=False)
    if not AlertFeed.is_unscheduled():
        embed.add_field(name=alert_header, value=alert_body, inline=False)
    embed.add_field(name='bumped.org', value=bumpedRSS.read(), inline=False)
    embed.add_field(name='pso2.jp/players/...', value=PSO2RSS.read())
    return (content, embed)
        
async def write_content(channel, body, embed):
    """Send the body with the embed into the channel.
    
    Edit the last known message if one is found, otherwise send a new message.
    
    Args:
        channel (str): ID of the channel to write into.
        body (str): Plain text of the message to be sent.
        embed (Embed): discord.Embed object to send with the body.
    
    """
    global channel_messages
    message = channel_messages[channel]
    fail_msg = 'Failed to send/edit message to channel:'
    try:
        if message == None:
            channel_messages[channel] = await channel.send(body, embed=embed)
        else: 
            await message.edit(content=body, embed=embed)
    except discord.errors.NotFound: 
        channel_messages[channel] = None
    except discord.errors.Forbidden:
        pass


