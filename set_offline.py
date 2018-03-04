import asyncio
import os

import discord
from   discord.ext import commands


import SLA_bot.config as cf
curr_dir = os.path.dirname(__file__)
default_config = os.path.join(curr_dir, 'default_config.ini'),
user_config = os.path.join(curr_dir, 'config.ini')
if not os.path.isfile(user_config):
    print("Could not find config at: \n{}".format(user_config))
    exit()
cf.load_configs(default_config, user_config)  

import SLA_bot.channelupdater as ChannelUpdater

prefix = cf.get('General', 'command_prefix')
bot = commands.Bot(command_prefix=prefix)

body = '''
[Hourly EQ](http://pso2emq.flyergo.eu/)
[Calendar (JST)](https://calendar.google.com/calendar/embed?src=pso2emgquest@gmail.com&mode=agenda)
[Official schedule](http://pso2.jp/players/boost/)'''

async def set_offline():
    ChannelUpdater.bot = bot
    await ChannelUpdater.load_channels() 
    embed=discord.Embed(title='Bot is offline.', color=0xdc4a4a)
    embed.add_field(name='--------------------', value=body)
    for channel, messages in ChannelUpdater.channel_messages.items():
        await ChannelUpdater.write_content(channel, ' ', embed)

@bot.event
async def on_ready():
    print('Logged in as: {}'.format(bot.user.name))
    print('------')
    await set_offline()
    await bot.logout()

bot.run(cf.get('General', 'bot_token'))


