import asyncio
import datetime as dt
import os

import discord
from   discord.ext import commands

import SLA_bot.channelupdater as ChannelUpdater
import SLA_bot.config as cf
import SLA_bot.constants as cs
import SLA_bot.module.pso2calendar as PSO2Calendar
import SLA_bot.module.pso2summary as PSO2Summary

tzone = cf.gettimezone('General', 'timezone')
def strfevent(event, ref_time):
    status = '{:>7}'.format(event.status(ref_time))
    range = event.time_range(tzone)
    return '`|{:^9}|` **{}** @ {}'.format(status, event.name, range)

class UserCommands:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help = cs.FIND_HELP)
    async def find(self, search='', mode=''):
        now = dt.datetime.now(dt.timezone.utc) 
        lsearch = search.lower()
        found = [x for x in PSO2Calendar.events if lsearch in x.name.lower()]
        num_found = len(found)
        max = cf.getint('General', 'max_find')
        if mode != 'all':
            found = found[:max]
                
        if found:
            lines = []
            summary = PSO2Summary.count_events(PSO2Calendar.events)
            for name, count in summary.items():
                if lsearch in name.lower():
                    lines.append('**{}** {}'.format(count, name))
            lines.append('')
            lines.extend([strfevent(event, now) for event in found])
            if len(found) < num_found:
                lines.append('...')
            msg = '\n'.join(lines)
        else:
            msg = 'No scheduled "{}" found.'.format(search or 'events') 
            
        if len(found) > max:
            await self.bot.whisper(msg[:2000])
        else:
            await self.bot.say(msg[:2000])

    @commands.command(help = cs.NEXT_HELP)
    async def next(self, search='',):
        now = dt.datetime.now(dt.timezone.utc)
        quest_length = dt.timedelta(minutes=30)
        started = [e for e in PSO2Calendar.events if e.start <= now]
        ongoing = [e for e in started if e.end - now <= quest_length]
        previous = [max(started, key=lambda e: e.end)] if started else []
        
        event_gap = dt.timedelta(minutes = 90)
        later = [e for e in PSO2Calendar.events if e.start > now]
        next = [e for e in later if e.start - later[0].start <= event_gap]

        found = previous + next
        if found:
            lines = [strfevent(event, now) for event in found]
            msg = '\n'.join(lines)
            await self.bot.say(msg[:2000])
        else:
            await self.bot.say('No more scheduled events.')

    @commands.command(pass_context=True, no_pm=True, help = cs.TOGGLE_HELP)
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