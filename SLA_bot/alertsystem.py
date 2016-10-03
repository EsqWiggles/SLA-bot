import asyncio
import datetime as dt
import json
import math
import sys
import traceback

import discord
from   discord.ext import commands

import SLA_bot.alertfeed as AlertFeed
import SLA_bot.constants as cs
from   SLA_bot.config import Config as cf
from   SLA_bot.gameevent import MultiShipEvent


class AlertChan:
    def __init__(self, id, filters, bot):
        self.bot = bot
        self.channel = bot.get_channel(id)
        self.filters = filters
        self.events = set()
        self.message = None
        self.last_send = None
        
    def add(self, events):
        self.events.update(events)

    def align_body(text):
        if not text:
            return ''
        lines = text.split('\n')
        header = lines[0]
        body = []
        for line in lines[1:]:
            body.append('`| {: >6} |` {}'.format('', line))
        return header + '\n' + '\n'.join(body)

    def split_events(events):
        upcoming = []
        passed = []
        now = dt.datetime.now(dt.timezone.utc)
        for e in sorted(events, key=lambda event: event.start, reverse=True):
            if e.start > now:
                upcoming.append(e)
            else:
                passed.append(e)
        return passed, upcoming
        
    def alert_text(self, events, ref_time):
        lines = []
        for e in events:
            text = e.duration(cf.tz)
            if getattr(e, 'unscheduled', False):
                text = MultiShipEvent.filter_ships(text, self.filters)
                text = AlertChan.align_body(text)
            if text == '':
                return ''
                
            time_left = math.ceil((e.start - ref_time).total_seconds() / 60)
            if time_left < 1:
                line = '`| {:->6} |` {}'.format('', text)
            else:
                hour, minute = divmod(time_left, 60)
                line = '`| {: >3}:{:0>2} |` {}'.format(hour, minute, text)
            lines.append(line)
        return '\n'.join(lines)
 
    async def edit(self, msg):
        self.message = await self.bot.edit_message(self.message, msg)
        
    async def send(self, msg):
        self.message = await self.bot.send_message(self.channel, msg)
        
    async def delete(self):
        await self.bot.delete_message(self.message)

    async def send_alert(self, passed, upcoming):
        now = dt.datetime.now(dt.timezone.utc)
        passed_text = self.alert_text(passed, now)
        upcoming_text = self.alert_text(upcoming, now)
        if self.message:
            if passed_text:
                await self.edit(passed_text)
            else:
                await self.delete()
            self.events = set(upcoming)
        if upcoming_text:
            await self.send(upcoming_text)
            self.send_new = False
            self.last_send = dt.datetime.now(dt.timezone.utc)
            
    async def edit_alert(self, passed, upcoming):
        now = dt.datetime.now(dt.timezone.utc)
        passed_text = self.alert_text(passed, now)
        upcoming_text = self.alert_text(upcoming, now)
        msg = '\n\n'.join((passed_text, upcoming_text))
        await self.edit(msg)
    
    def should_resend(self, events, time_span):
        if self.last_send == None:
            return True
        now = dt.datetime.now(dt.timezone.utc)
        for e in events:
            resend_time = e.start - time_span
            if resend_time <= now and resend_time > self.last_send:
                return True
        return False
    
    async def update(self):
        if len(self.events) < 1:
            return
            
        passed, upcoming = AlertChan.split_events(self.events)
        if self.should_resend(upcoming, cf.resend_before):
            await self.send_alert(passed, upcoming)
        else:
            await self.edit_alert(passed, upcoming)

class AlertSystem:
    """Manages alerts for events and emergency quests.
    """
    def __init__(self, bot, schedule):
        self.bot = bot
        self.schedule = schedule
        self.achans = []
        self.feeds = []
        for chan in cf.channels:
            self.achans.append(AlertChan(chan[0], chan[1], bot))

    async def feed_update(self):
        url = 'http://pso2emq.flyergo.eu/api/v2/'
        last_update = None
        while not self.bot.is_closed:
            try:
                now = dt.datetime.now(dt.timezone.utc)
                data = await AlertFeed.download(url)
                if len(data) > 0 and data[0]['jst'] != last_update:
                    self.feeds = AlertFeed.parse_notices(data, now)
                    last_update = data[0]['jst']
            except json.decoder.JSONDecodeError:
                pass
            except Exception:
                print('Ignored following error:')
                print(traceback.format_exc(), file=sys.stderr)
            await asyncio.sleep(60)
        
    async def update(self):
        while not self.bot.is_closed:
            now = dt.datetime.now(dt.timezone.utc)
            alert_to = now + cf.alert_before
            try:
                if cf.enable_alert:
                    upcoming = self.schedule.from_range(now, alert_to)
                    unscheduled = [x for x in self.feeds if x.unscheduled]
                    upcoming.extend([x for x in unscheduled if x.start > now])
                    for chan in self.achans:
                        chan.add(upcoming)
                        await chan.update()
            except Exception:
                print('Ignored following error:')
                print(traceback.format_exc(), file=sys.stderr)
            await asyncio.sleep(60 - now.second)
            
    def add_channel(self, id, filters):
        for achan in self.achans:
            if achan.channel and achan.channel.id == id:
                cf.set_chan(id, filters)
                for c in cf.channels:
                    if c[0] == id:
                        achan.filters = c[1]
                return
    
        cf.set_chan(id, filters)
        filters =''
        for c in cf.channels:
            if c[0] == id:
                filters = c[1]
        
        achan = AlertChan(id, filters, self.bot)
        self.achans.append(achan)

    def delete_channel(self, id):
        i = len(self.achans)
        for i, achan in enumerate(self.achans):
            if achan.channel and achan.channel.id == id:
                cf.delete_chans([id])
                break
        if i < len(self.achans):
            self.achans.pop(i)
            
    @commands.command(help=cs.ALLRANDOM_HELP)
    async def allrandom(self, chosen='1,2,3,4,5,6,7,8,9,10'):
        now = dt.datetime.now(cf.tz)
        curr_time = '**Now: ** {}\n\n'.format(now.strftime('%b %d, %H:%M %Z'))
        await self.bot.whisper(curr_time)
        
        chosen_ships = [int(x) for x in chosen.split(',')]
        filters = [x for x in range(1,11) if x not in chosen_ships]
        divider = '.\n'
        for alert in self.feeds:
            if alert.unscheduled:
                text = alert.duration(cf.tz)
                text = MultiShipEvent.filter_ships(text, filters)
                await self.bot.whisper(divider + text)

    @commands.command(pass_context=True, no_pm=True, help=cs.SET_ALERTS_HELP)
    async def set_alerts(self, ctx, filters='0'):
        perm = ctx.message.channel.permissions_for(ctx.message.author)
        id = ctx.message.channel.id
        if perm.manage_channels:
            self.add_channel(id, filters)
            
    @commands.command(pass_context=True, no_pm=True, help=cs.REMOVE_ALERTS_HELP)
    async def remove_alerts(self, ctx):
        perm = ctx.message.channel.permissions_for(ctx.message.author)
        id = ctx.message.channel.id
        if perm.manage_channels:
            self.delete_channel(id)
            
    @commands.command(hidden=True, enabled=False, help='')
    async def remove_unreachable(self):
        #needs user must be owner, enable when implemented
        unreachable = []
        for i, achan in enumerate(self.achans):
            if achan and not achan.channel:
                unreachable.append(i)
        for i in unreachable:
            self.achans.pop(i)
        
        deleted = []
        for chan in cf.channels:
            id = chan[0]
            if self.bot.get_channel(id) == None:
                deleted.append(id)
        cf.delete_chans(deleted)
            
    @commands.command(pass_context=True, no_pm=True, help = cs.RESEND_HELP)
    async def resend(self, ctx):
        curr_chan = ctx.message.channel
        for achan in self.achans:
            if achan.channel == curr_chan:
                passed, upcoming = AlertChan.split_events(achan.events)
                await achan.send_alert(passed, upcoming)
                break
