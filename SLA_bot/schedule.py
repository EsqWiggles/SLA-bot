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
import SLA_bot.util as ut

class Schedule:
    def __init__(self, bot):
        self._events = []
        self.bot = bot
                    
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
                
    async def grab_events(self, cal_path, from_dt, to_dt=None):
        current_events = []
        with open(cal_path, 'rb') as cal_file:
            gcal = ical.Calendar.from_ical(cal_file.read())
            for component in gcal.walk():
                if component.name == "VEVENT":
                    start_dt = component.get('dtstart').dt
                    if start_dt >= from_dt and (to_dt == None or start_dt <= to_dt):
                        current_events.append(component)
        current_events.sort(key=lambda event: event.get('dtstart').dt)
        self._events = current_events

    def prev_maint():
        m_time = dt.datetime.strptime(cf.wkstart_time, '%H:%M:%S')
        return ut.prev_weekday(cf.wkstart_weekday, m_time)
    
    async def update(self):
        downloaded = await Schedule.download(cf.cal_url, cf.cal_path)
        if downloaded == True:
            await self.grab_events(cf.cal_path, Schedule.prev_maint())
    
    async def filter_events(self, earliest=None, latest=None):
        events = []
        for e in self._events:
            start_time = e.get('dtstart').dt
            if earliest != None and start_time < earliest:
                 continue
            if latest != None and start_time >= latest :
                 continue
            events.append(e)
        return events
    
    async def qsay(self, message):
        await ut.quiet_say(self.bot, message, cf.max_line)
    
    def strfschedule(events, tz):
        event_days=[]
        prev_date = None

        for e in reversed(events):
            start_time = e.get('dtstart').dt.astimezone(tz)
            if start_time.date() != prev_date:
                day_header = start_time.strftime('%A %Y-%m-%d %Z\n')
                day_header += '================================'
                event_days.append(day_header)
                prev_date = start_time.date()
                
            name = e.get('summary')
            start_str = start_time.strftime('%H:%M:%S')
            single_event = ('\n{0} | {1}'.format(start_str, name))
            event_days[-1] += single_event
        return event_days

    async def print_schedule(self, events, tz):
        days = Schedule.strfschedule(events, tz)
        for i in range(len(days)):
            days[i] = '```{}```'.format(days[i])
        await self.qsay(days)
    
    def find_event(events, search='', max=-1, custom=None):
        found = []
        count = 0
        for e in events:
            if count >= max and max != -1:
                break;
            
            searches = []
            try:
                searches = custom[search]
            except (KeyError, TypeError):
                searches.append(search)

            for s in searches:
                if s.lower() in e.get('summary').lower():
                    found.append(e)
                    count += 1
                    break;
        return found
    
    def relstr_event(events, tz):
        events_str = []
        now = dt.datetime.now(dt.timezone.utc)
        for e in events:
            name = e.get('summary')
            start = e.get('dtstart').dt
            start_str = start.astimezone(tz).strftime('%b %d   %H:%M %Z')
            diff = start - now
            relative = ut.strfdelta(abs(diff))
            if diff >= dt.timedelta(0):
                e_str = 'In {} - **{}** - {}'.format(relative, name, start_str)
            else:
                e_str = '{} ago - **{}** - {}'.format(relative, name, start_str)
            events_str.append(e_str)
        return events_str
    
    
    @commands.command()
    async def eq_print(self, mode='today', tz_str=None):
        timezone = ut.parse_tz(tz_str, cf.tz, cf.custom_tz)

        today = ut.day(dt.datetime.now(timezone), 0, timezone)
        if mode == 'today':
            events = await self.filter_events(today, ut.day(today, 1, timezone))
        elif mode == 'yesterday':
            events = await self.filter_events(ut.day(today, -1, timezone), today)
        elif mode == 'tomorrow':
            events = await self.filter_events(ut.day(today, 1, timezone), ut.day(today, 2, timezone))
        elif mode == 'past':
            events = await self.filter_events(latest = dt.datetime.now(dt.timezone.utc))
        elif mode == 'future':
            events = await self.filter_events(earliest = dt.datetime.now(dt.timezone.utc))
        elif mode == 'all':
            events = await self.filter_events()
        else:
            dates = ut.parse_md(mode, timezone)
            events = []
            for d in dates:
                events.extend(await self.filter_events(d, ut.day(d, 1, timezone)))
        await self.print_schedule(events, timezone)

    @commands.command()
    async def find(self, search='', mode='future', tz_str=''):
        timezone = ut.parse_tz(tz_str, cf.tz, cf.custom_tz)
        events = []
        if mode == 'past':
            events = await self.filter_events(latest = dt.datetime.now(dt.timezone.utc))
        elif mode == 'future':
            events = await self.filter_events(earliest = dt.datetime.now(dt.timezone.utc))
        elif mode == 'all':
            events = await self.filter_events()
        matched = Schedule.find_event(events, search, -1, cf.alias)
        messages = Schedule.relstr_event(matched, timezone)
        await self.qsay(messages)
            
        
    @commands.command()
    async def next(self, search='', tz_str=''):
        timezone = ut.parse_tz(tz_str, cf.tz, cf.custom_tz)
        now = dt.datetime.now(dt.timezone.utc)
        upcoming = await self.filter_events(earliest = now)
        matched = Schedule.find_event(upcoming, search.lower(), 1, cf.alias)
        
        if len(matched) >= 1:
            msg = Schedule.relstr_event(matched, timezone)[0]
        else:
            msg = 'No scheduled {} found.'.format(search)

        await self.qsay(msg)
        
        
    @commands.command()
    async def last(self, search='', tz_str=''):
        timezone = ut.parse_tz(tz_str, cf.tz, cf.custom_tz)
        now = dt.datetime.now(dt.timezone.utc)
        upcoming = await self.filter_events(latest = now)
        upcoming.reverse()
        matched = Schedule.find_event(upcoming, search.lower(), 1, cf.alias)
        
        if len(matched) >= 1:
            msg = Schedule.relstr_event(matched, timezone)[0]
        else:
            msg = 'No scheduled {} found.'.format(search)

        await self.qsay(msg)
