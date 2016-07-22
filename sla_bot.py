import asyncio

import discord
from   discord.ext import commands



bot = commands.Bot(command_prefix='!', description='test')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    
@bot.command()
async def test():
    await bot.say('Hello World!')

bot.run('paste_token_here')
