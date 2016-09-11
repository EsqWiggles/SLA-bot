import asyncio
import datetime as dt
import math

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
        self.events = []
        self.message = None
        self.last_send = None
        self.send_new = True
        self._update_task = bot.loop.create_task(self.updater())
        
    def add(self, events):
        if len(events) < 1:
            return

        for e in events:
            self.events.append(e)
        self.events.sort(key=lambda event: event.start, reverse=True)

    def align_body(text):
        if not text:
            return ''
        lines = text.split('\n')
        header = lines[0]
        body = []
        for line in lines[1:]:
            body.append('`| {: >6} |` {}'.format('', line))
        return header + '\n' + '\n'.join(body)

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
                line = '`| {: >3}min |` {}'.format(time_left, text)
            lines.append(line)
        return '\n'.join(lines)
 
    async def edit(self, msg):
        self.message = await self.bot.edit_message(self.message, msg)
        
    async def send(self, msg):
        self.message = await self.bot.send_message(self.channel, msg)
        
    async def delete(self):
        await self.bot.delete_message(self.message)
        
    def split_events(self):
        upcoming = []
        passed = []
        now = dt.datetime.now(dt.timezone.utc)
        for e in self.events:
            if e.start > now:
                upcoming.append(e)
            else:
                passed.append(e)
        return upcoming, passed
        
    async def send_alert(self):
        now = dt.datetime.now(dt.timezone.utc)
        upcoming, passed = self.split_events()
        passed_text = self.alert_text(passed, now)
        upcoming_text = self.alert_text(upcoming, now)
        if self.message:
            if passed_text:
                await self.edit(passed_text)
            else:
                await self.delete()
            self.events = upcoming
        if upcoming_text:
            await self.send(upcoming_text)
            self.send_new = False
            
    async def update_alert(self):
        now = dt.datetime.now(dt.timezone.utc)
        upcoming, passed = self.split_events()
        passed_text = self.alert_text(passed, now)
        upcoming_text = self.alert_text(upcoming, now)
        msg = '\n\n'.join((passed_text, upcoming_text))
        await self.edit(msg)
        
    def check_resend(self, time_span):
        if self.send_new == True:
            return
        now = dt.datetime.now(dt.timezone.utc)
        upcoming = [x for x in self.events if x.start > now]
        for e in upcoming:
            if e.start - now <= time_span:
                if self.last_send == None or e.start > self.last_send:
                    self.send_new = True
                    self.last_send = e.start
    
    async def update(self):
        if len(self.events) < 1:
            return

        self.check_resend(cf.alert_every)
        if self.send_new:
            await self.send_alert()
        else:
            await self.update_alert()
            
    async def updater(self):
        while not self.bot.is_closed:
            try:
                await self.update()
            except (discord.errors.HTTPException, discord.errors.Forbidden):
                continue
            except (discord.errors.NotFound, discord.errors.InvalidArgument):
                break
            now = dt.datetime.now(dt.timezone.utc)
            await asyncio.sleep(60 - now.second)
            
    def stop_updater(self):
        self._update_task.cancel()

class AlertSystem:
    """Manages alerts for events and emergency quests.
    """
    def __init__(self, bot, schedule):
        self.bot = bot
        self.schedule = schedule
        self.achans = []
        self.feeds = []
        self._last_sched_time = None
        self._last_feed_time = None
        
        for chan in cf.channels:
            self.achans.append(AlertChan(chan[0], chan[1], bot))

    def from_schedule(self):
        if self.schedule.edir == None:
            return []
        now = dt.datetime.now(dt.timezone.utc)
        last_update = self._last_sched_time
        alert_from = last_update if last_update else now
        alert_to = now + cf.alert_before
        self._last_sched_time = alert_to
        return self.schedule.from_range(alert_from, alert_to)

    async def feed_update(self):
        url = 'http://pso2emq.flyergo.eu/api/v2/'
        last_update = None
        while not self.bot.is_closed:
            now = dt.datetime.now(dt.timezone.utc)
            data = await AlertFeed.download(url)
            if len(data) > 0 and data[0]['jst'] != last_update:
                self.feeds = AlertFeed.parse_notices(data, now)
                last_update = data[0]['jst']
            await asyncio.sleep(60)
            
    def from_feed(self):
        if self.feeds == None or len(self.feeds) < 1:
            return []

        now = dt.datetime.now(dt.timezone.utc)
        last_update = self._last_feed_time
        most_recent = self.feeds[0].start
        if last_update != most_recent:
            self._last_feed_time = most_recent
            if most_recent > now:
                return [self.feeds[0]]
        return []
        
    async def update(self):
        last_update = None
        while not self.bot.is_closed:
            new_events = []
            unscheduled = [x for x in self.from_feed() if x.unscheduled]
            new_events.extend(self.from_schedule())
            new_events.extend(unscheduled)

            if len(new_events) > 0:
                for chan in self.achans:
                    chan.add(new_events)
            now = dt.datetime.now(dt.timezone.utc)
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
        now = dt.datetime.now(dt.timezone.utc)
        new_events = self.schedule.from_range(now, self._last_sched_time)
        if self.feeds and len(self.feeds) > 1:
            latest_feed = self.feeds[0]
            if latest_feed.unscheduled:
                new_events.extend([latest_feed])
        achan.add(new_events)
        self.achans.append(achan)

    def delete_channel(self, id):
        i = len(self.achans)
        for i, achan in enumerate(self.achans):
            if achan.channel and achan.channel.id == id:
                achan.stop_updater()
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
                await achan.send_alert()
                break
        
        