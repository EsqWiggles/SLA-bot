import asyncio
import datetime as dt
import math

import discord

import SLA_bot.alertfeed as AlertFeed
from   SLA_bot.config import Config as cf


class AlertChan:
    def __init__(self, id, targets, bot):
        self.bot = bot
        self.channel = bot.get_channel(id)
        self.targets = targets
        self.events = []
        self.message = None
        self.last_send = None
        
    def add(self, events):
        if len(events) < 1:
            return

        for e in events:
            self.events.append(e)
        self.events.sort(key=lambda event: event.start, reverse=True)
    
    def align_body(text):
        lines = text.split('\n')
        header = lines[0]
        body = []
        for line in lines[1:]:
            body.append('`| {: >6} |` {}'.format('', line))
        return header + '\n' + '\n'.join(body)
        
        
    
    def alert_text(self, events, ref_time):
        lines = []
        for e in events:
            time_left = math.ceil((e.start - ref_time).total_seconds() / 60)
            if hasattr(e, 'multi_dur'):
                text = e.multi_dur(self.targets, cf.tz)
                if e.unscheduled:
                    text = AlertChan.align_body(text)
            else:
                text = e.duration(cf.tz)
                
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
    
    async def update(self, resend):
        if len(self.events) < 1:
            return

        now = dt.datetime.now(dt.timezone.utc)
        passed, upcoming = [], []
        for e in self.events:
            if e.start > now:
                upcoming.append(e)
            else:
                passed.append(e)
                
        send_new = False if self.message else True
        if send_new == False:
            for e in upcoming:
                if e.start - now <= resend:
                    if self.last_send == None or e.start > self.last_send:
                        send_new = True
                        self.last_send = e.start
       
        passed_text = self.alert_text(passed, now)
        upcoming_text = self.alert_text(upcoming, now)
        
        if send_new:
            if self.message:
                #delete instead of edit
                await self.edit(passed_text)
            #don't send if nothing
            await self.send(upcoming_text)
            send_new = False
        else:
            msg = '\n\n'.join((passed_text, upcoming_text))
            await self.edit(msg)

            
    async def updater(self):
        while not self.bot.is_closed:
            try:
                await self.update(cf.alert_every)
            except (discord.errors.HTTPException, discord.errors.Forbidden):
                continue
            except (discord.errors.NotFound, discord.errors.InvalidArgument):
                break
            now = dt.datetime.now(dt.timezone.utc)
            await asyncio.sleep(60 - now.second)

class AlertSystem:
    def __init__(self, bot, schedule):
        self.bot = bot
        self.schedule = schedule
        self.achans = []
        self.feeds = []
        self._last_sched_time = None
        self._last_feed_time = None
        
        for chan in cf.channels:
            a = AlertChan(chan[0], chan[1], bot)
            bot.loop.create_task(a.updater())
            self.achans.append(a)

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

