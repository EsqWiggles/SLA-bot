import asyncio
import datetime as dt
import math
import os
import sys

import aiohttp
from   discord.ext import commands
import icalendar as ical
import pytz

import SLA_bot.constants as cs
from   SLA_bot.config import Config as cf
from   SLA_bot.eventdir import EventDir
from   SLA_bot.gameevent import GameEvent
import SLA_bot.util as ut

class Schedule:
    """Provides methods to find and print scheduled events.
    None of these commands will display unscheduled events!
    """
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
    
    def strfschedule(self, events, tz):
        event_days=[]
        prev_date = None
        try:
            next_time = self.edir.events[self.edir.next].start
        except IndexError:
            next_time = dt.datetime.now(dt.timezone.utc)
        for e in events:
            start_time = e.start.astimezone(tz)
            if start_time.date() != prev_date:
                day_header = start_time.strftime('%A %Y-%m-%d %Z\n')
                day_header += '================================'
                event_days.append(day_header)
                prev_date = start_time.date()
                
            start_str = start_time.strftime('%H:%M')
            prefix = '-> ' if e.start == next_time else '   '
            single_event = ('\n{}{} | {}'.format(prefix, start_str, e.name))
            event_days[-1] += single_event
        return event_days

    async def print_schedule(self, events, tz):
        days = self.strfschedule(events, tz)
        for i in range(len(days)):
            days[i] = '```{}```'.format(days[i])
        await self.qsay(days)
    
    def find_idx(self, search='', custom=None):
        found = []
        try:
            searches = custom[search.lower()]
        except (KeyError, TypeError):
            searches = [search.lower()]

        for s in searches:
            found.extend(self.edir.find(s))
        found = list(set(found))
        found.sort()
        return found
        
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

    @commands.command(help = cs.PRINT_HELP)
    async def print(self, date='today', timezone=''):
        date = date.lower()
        tz = ut.parse_tz(timezone, cf.tz, cf.custom_tz)
        today = ut.day(dt.datetime.now(tz), 0, tz)
        yesterday = ut.day(today, -1, tz)
        tomorrow = ut.day(today, 1, tz)
        day_after = ut.day(today, 2, tz)
        if date == 'today':
            events = self.from_range(today, tomorrow)
        elif date == 'yesterday':
            events = self.from_range(yesterday, today)
        elif date == 'tomorrow':
            events = self.from_range(tomorrow, day_after)
        elif date == 'future':
            events = self.from_range(earliest = dt.datetime.now(dt.timezone.utc))
        elif date == 'week':
            events = self.from_range(earliest = Schedule.prev_maint())
        else:
            events = []
            dates = ut.parse_date(date, tz)
            for d in reversed(dates):
                events = self.from_range(d, ut.day(d, 1, tz))
                if len(events) > 0:
                    break
        await self.print_schedule(events, tz)

    @commands.command(help = cs.FUTURE_HELP)
    async def future(self, search='', timezone=''):
        tz = ut.parse_tz(timezone, cf.tz, cf.custom_tz)
        if search == '':
            start = self.edir.next
            end = start + cf.find_default
            found = self.edir.events[start:end]
        else:
            matched = self.find_idx(search, cf.alias)
            upcoming = [x for x in matched if x >= self.edir.next]
            found = self.edir.eventsfidx(upcoming)
        if len(found) > 0:
            messages = Schedule.relstr_event(found, tz)
        else:
            messages = ['No scheduled {} found.'.format(search or 'events')]
        await self.qsay(messages)
            
    @commands.command(help = cs.NEXT_HELP)
    async def next(self, search='', timezone=''):
        tz = ut.parse_tz(timezone, cf.tz, cf.custom_tz)
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
            events = self.edir.connected(next_idx, cf.linked_time)
            msg = Schedule.relstr_event(events, tz)
        await self.qsay(msg)

    @commands.command(help = cs.LAST_HELP)
    async def last(self, search='', timezone=''):
        tz = ut.parse_tz(timezone, cf.tz, cf.custom_tz)
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
            events = self.edir.connected(last_idx, cf.linked_time)
            msg = Schedule.relstr_event(events, tz)
        await self.qsay(msg)

