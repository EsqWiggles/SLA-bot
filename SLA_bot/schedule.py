import asyncio
import datetime as dt
import math
import os
import sys

import aiohttp
from   discord.ext import commands
import icalendar as ical
import pytz

from   SLA_bot.config import Config as cf
from   SLA_bot.eventdir import EventDir
from   SLA_bot.gameevent import GameEvent
import SLA_bot.util as ut

class Schedule:
    def __init__(self, bot):
        self._events = []
        self.bot = bot
        self.edir = None
                    
    async def download(url, save_path):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        async with aiohttp.get(url) as response:
            if response.status == 200:
                with open(save_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(cf.chunk_size)
                        if not chunk:
                            break
                        file.write(chunk)
                
                #check if a valid ical file too?
                if os.path.isfile(save_path):
                    return True
            else:
                print('File could not be downloaded. Recieved HTTP code {} {}'.format(response.status, response.reason), file=sys.stderr)
        return False
                
    async def parse_calendar(self, cal_path):
        events = []
        with open(cal_path, 'rb') as cal_file:
            cal = ical.Calendar.from_ical(cal_file.read())
            for component in cal.walk():
                if component.name == "VEVENT":
                    events.append(GameEvent.from_ical(component))
        events.sort(key=lambda event: event.start)
        return EventDir(events)

    def prev_maint():
        m_time = dt.datetime.strptime(cf.wkstart_time, '%H:%M:%S')
        return ut.prev_weekday(cf.wkstart_weekday, m_time)
    
    async def update(self):
        downloaded = await Schedule.download(cf.cal_url, cf.cal_path)
        if downloaded == True:
            self.edir = await self.parse_calendar(cf.cal_path)
    
    def from_range(self, earliest=None, latest=None):
        start, upto = self.edir.rangefdt(earliest, latest)
        return self.edir.events[start:upto]
    
    async def qsay(self, message):
        await ut.quiet_say(self.bot, message, cf.max_line)
    
    def strfschedule(events, tz):
        event_days=[]
        prev_date = None

        for e in reversed(events):
            start_time = e.start.astimezone(tz)
            if start_time.date() != prev_date:
                day_header = start_time.strftime('%A %Y-%m-%d %Z\n')
                day_header += '================================'
                event_days.append(day_header)
                prev_date = start_time.date()
                
            start_str = start_time.strftime('%H:%M:%S')
            single_event = ('\n{0} | {1}'.format(start_str, e.name))
            event_days[-1] += single_event
        return event_days

    async def print_schedule(self, events, tz):
        days = Schedule.strfschedule(events, tz)
        for i in range(len(days)):
            days[i] = '```{}```'.format(days[i])
        await self.qsay(days)
    
    def find_idx(self, search='', custom=None):
        found = []
        try:
            searches = custom[search]
        except (KeyError, TypeError):
            searches = [search]

        for s in searches:
            found.extend(self.edir.find(s))
        found = list(set(found))
        found.sort()
        return found
        
    def eventsfidx(events, indices):
        new_list = []
        for i in indices:
            new_list.append(events[i])
        return new_list

    def relstr_event(events, tz):
        events_str = []
        now = dt.datetime.now(dt.timezone.utc)
        for e in events:
            diff = e.start - now
            relative = ut.strfdelta(abs(diff))
            if diff >= dt.timedelta(0):
                e_str = 'In {} - {}'.format(relative, e.duration(tz))
            else:
                e_str = '{} ago - {}'.format(relative, e.duration(tz))
            events_str.append(e_str)
        return events_str


    def connected(events, idx, timeframe):
        linked = [events[idx]]
        for i in range(idx + 1, len(events)):
            last_start = linked[-1].start
            curr_start = events[i].start
            if abs(curr_start - last_start) > timeframe:
                break;
            linked.append(events[i])
        return linked
            
    
    @commands.command()
    async def eq_print(self, mode='today', tz_str=None):
        timezone = ut.parse_tz(tz_str, cf.tz, cf.custom_tz)

        today = ut.day(dt.datetime.now(timezone), 0, timezone)
        maint_time = Schedule.prev_maint()
        if mode == 'today':
            events = self.from_range(today, ut.day(today, 1, timezone))
        elif mode == 'yesterday':
            events = self.from_range(ut.day(today, -1, timezone), today)
        elif mode == 'tomorrow':
            events = self.from_range(ut.day(today, 1, timezone), ut.day(today, 2, timezone))
        elif mode == 'past':
            events = self.from_range(maint_time, dt.datetime.now(dt.timezone.utc))
        elif mode == 'future':
            events = self.from_range(earliest = dt.datetime.now(dt.timezone.utc))
        elif mode == 'all':
            events = self.from_range(maint_time, dt.datetime.now(dt.timezone.utc))
        else:
            events = []
            dates = ut.parse_md(mode, timezone)
            for d in reversed(dates):
                events = self.from_range(d, ut.day(d, 1, timezone))
                if len(events) > 0:
                    break
        await self.print_schedule(events, timezone)

    @commands.command()
    async def find(self, search='', mode='future', tz_str=''):
        timezone = ut.parse_tz(tz_str, cf.tz, cf.custom_tz)
        matched = self.find_idx(search, cf.alias)
        after_maint = self.edir.rangefdt(start = Schedule.prev_maint())[0]
        if mode == 'past':
            matched = [x for x in matched if x >= after_maint and x < self.edir.next]
        elif mode == 'future':
            matched = [x for x in matched if x >= self.edir.next]
        elif mode == 'all':
            matched = [x for x in matched if x >= after_maint]
        
        found = Schedule.eventsfidx(self.edir.events, matched)
        messages = Schedule.relstr_event(found, timezone)
        await self.qsay(messages)
            
        
    @commands.command()
    async def next(self, search='', tz_str=''):
        timezone = ut.parse_tz(tz_str, cf.tz, cf.custom_tz)
        if search == '':
            next_idx = self.edir.next
        else:
            found = self.find_idx(search, cf.alias)
            found = [x for x in found if x >= self.edir.next]
            try:
                next_idx = found[0]
            except IndexError:
                next_idx = self.edir.end
        if next_idx == self.edir.end:
            msg = 'No scheduled {} found.'.format(search or 'events')
        else:
            events = Schedule.connected(self.edir.events, next_idx, cf.linked_time)
            msg = Schedule.relstr_event(events, timezone)
        await self.qsay(msg)

    @commands.command()
    async def last(self, search='', tz_str=''):
        timezone = ut.parse_tz(tz_str, cf.tz, cf.custom_tz)
        if search == '':
            last_idx = self.edir.last
        else:
            found = self.find_idx(search, cf.alias)
            found = [x for x in found if x < self.edir.next]
            try:
                last_idx = found[-1]
            except IndexError:
                last_idx = self.edir.end
        if last_idx == self.edir.end:
            msg = 'No old scheduled {} found.'.format(search or 'events')
        else:
            events = Schedule.connected(self.edir.events, last_idx, cf.linked_time)
            msg = Schedule.relstr_event(events, timezone)
        await self.qsay(msg)

