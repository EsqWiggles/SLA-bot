"""Run Discord bot to aggregate supplementary resources for PSO2

Example:
    This bot must be run on python 3.5 or later. Depending on your system,
    python, python3, or python3.5 should be used. Because the bot is
    generally left on for long periods of time, you may want to save the
    stderr to a file to check for errors.
        $ python sla_bot.py
        $ python3 sla_bot.py 
        $ python3 sla_bot.py 2>> error.log
"""
import asyncio
import datetime as dt
import os

import discord
from   discord.ext import commands

#Load config first so other project files can save config vars at module level
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
from   SLA_bot.commands import UserCommands
import SLA_bot.constants as cs
import SLA_bot.util as ut




VERSION = 0.34

prefix = cf.get('General', 'command_prefix')
tzone = cf.gettimezone('General', 'timezone')
initialized = False
bot = commands.Bot(command_prefix=prefix, pm_help=True, description=cs.BOT_HELP)
bot.add_cog(UserCommands(bot))

async def bot_status(bot):
    """Run a clock on the bot's status line."""
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

@bot.event
async def on_ready():
    print('Logged in as: {}'.format(bot.user.name))
    print('------')
    
    #This method may be called more than once
    global initialized
    if not initialized:
        await ChannelUpdater.init(bot)
        bot.loop.create_task(bot_status(bot))
        initialized = True


bot.run(cf.get('General', 'bot_token'))
