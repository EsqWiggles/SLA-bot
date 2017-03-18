import asyncio
import collections
import datetime as dt
import sys
import traceback

import discord

import SLA_bot.config as cf
from   SLA_bot.alertfeed import AlertFeed
from   SLA_bot.clock import Clock
from   SLA_bot.pso2calendar import PSO2Calendar

class ChannelUpdater:
    def __init__(self, bot):
        self.bot = bot
        self.channel_messages = {}
        self.modules = collections.OrderedDict()
        self.modules[Clock] = 'No data'
        self.modules[AlertFeed] = 'No data'
        self.modules[PSO2Calendar] = 'No data'
    
    
    async def recyle_messages(self, channel):
        wanted = len(self.modules)
        try:
            messages = self.bot.logs_from(channel, limit=wanted, reverse=True)
            recyled = []
            async for msg in messages:
                if msg.author.id == self.bot.user.id:
                    recyled.append(msg)
                else:
                    break
            return recyled
        except (discord.errors.Forbidden, discord.errors.NotFound):
            return []

        
    async def write_content(self, channel, nth_msg, content):
        m = self.channel_messages[channel]
        c = content[:2000]
        try:
            m[nth_msg] = await self.bot.edit_message(m[nth_msg], c)
        except IndexError:
            try:
                new_msg = await self.bot.send_message(channel, c)
                m.append(new_msg)
                self.channel_messages[channel] = await self.recyle_messages(channel)
            except (discord.errors.Forbidden, discord.errors.NotFound):
                pass
        except discord.errors.NotFound:
            del m[nth_msg]
        
    async def updater(self, contentFunc, nth_msg, interval):
        while not self.bot.is_closed:
            try:
                content = await contentFunc()
                for channel in self.channel_messages:
                    await self.write_content(channel, nth_msg, content)
            except Exception:
                print('Ignored following error:')
                print(traceback.format_exc(), file=sys.stderr)
            await asyncio.sleep(interval)
            
    async def load_channels(self):
        for c in cf.channels():
            chan = self.bot.get_channel(c)
            self.channel_messages[chan] = await self.recyle_messages(chan)
            
    async def make_updaters(self):
        await self.load_channels()
        clock_i = cf.getint('Clock', 'update_interval')
        feed_i = cf.getint('PSO2 Feed', 'update_interval')
        cal_i = cf.getint('PSO2 Calendar', 'update_interval')
        self.bot.loop.create_task(self.updater(Clock.fetch, 0, clock_i))
        self.bot.loop.create_task(self.updater(AlertFeed.fetch, 1, feed_i))
        self.bot.loop.create_task(self.updater(PSO2Calendar.fetch, 2, cal_i))