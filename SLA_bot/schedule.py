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
    
    
    def prev_weekday(weekday, at):
        curr = dt.datetime.now(dt.timezone.utc)
        prev = curr.replace(hour=at.hour, minute=at.minute,
                            second=at.second, microsecond=0)
        while(prev >= curr or prev.isoweekday() != weekday):
            prev = prev - dt.timedelta(days=1)
        return prev

    def prev_maint():
        m_time = dt.datetime.strptime(cf.wkstart_time, '%H:%M:%S')
        return Schedule.prev_weekday(cf.wkstart_weekday, m_time)
    
    async def update(self):
        downloaded = await Schedule.download(cf.cal_url, cf.cal_path)
        if downloaded == True:
            await self.grab_events(cf.cal_path, Schedule.prev_maint())
            
    def utctz_offset(offset):
        h,sep,m = offset.partition(':')
        h = int(h)
        sign = 1
        if h < 0:
            sign = -1
        if m == '':
            m = 0
        else:
            m = int(m)
        m = sign * m
        utc_tz = dt.timezone(dt.timedelta(hours=h, minutes=m))
        return utc_tz
            
    def parse_tz(tz_str, default_tz=None, custom=None):
        if tz_str == None or tz_str == '':
            return default_tz
        
        try:
            return Schedule.utctz_offset(tz_str)
        except ValueError:
            pass
    
        if custom != None:
            custom_tz = tz_str.lower()
            if custom_tz in custom:
                return pytz.timezone(custom[custom_tz])
                
        country_code = tz_str.upper()
        if country_code in pytz.country_timezones:
            return pytz.timezone(pytz.country_timezones[country_code][0])

        try:
            return pytz.timezone(tz_str)
        except pytz.exceptions.UnknownTimeZoneError:
            return None
  
        return None
    
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
    
    async def event_print(self, events, tz=None):
        if tz == None:
            tz = pytz.timezone(cf.tz)

        prev_date = None
        msg_chunk = None

        for e in reversed(events):
            start_time = e.get('dtstart').dt.astimezone(tz)
            name = e.get('summary')
            start_str = start_time.strftime('%H:%M:%S')
            msg = ('\n{0} | {1}'.format(start_str, name))
            if start_time.date() != prev_date:
                if msg_chunk != None:
                    await self.bot.say('```{}```'.format(msg_chunk))
                msg_chunk = start_time.strftime('%A %Y-%m-%d %Z\n')
                msg_chunk += '================================'
                prev_date = start_time.date()
            msg_chunk += msg

        await self.bot.say('```{}```'.format(msg_chunk))
    
    def find_event(events, search='', max=-1):
        found = []
        count = 0
        for e in events:
            if search in e.get('summary').lower():
                found.append(e)
                count += 1
                if count >= max and max != -1:
                    break;
        return found
    
    def relstr_event(events, tz):
        events_str = []
        now = dt.datetime.now(dt.timezone.utc)
        for e in events:
            name = e.get('summary')
            start = e.get('dtstart').dt
            relative = ut.strfdelta(start - now)
            start_str = start.astimezone(tz).strftime('%b %d   %H:%M %Z')
            e_str = 'In {} - **{}** - {}'.format(relative, name, start_str)
            events_str.append(e_str)
        return events_str
    
    
    @commands.command()
    async def eq_print(self, mode='today', tz_str=None):
        default = pytz.timezone(cf.tz)
        timezone = Schedule.parse_tz(tz_str, default, cf.custom_tz)
        if timezone == None:
            return

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
        await self.event_print(events, timezone)

    @commands.command()
    async def find(self, search='', mode='future', tz_str=''):
        default = pytz.timezone(cf.tz)
        timezone = Schedule.parse_tz(tz_str, default, cf.custom_tz)
        events = []
        if mode == 'past':
            events = await self.filter_events(latest = dt.datetime.now(dt.timezone.utc))
        elif mode == 'future':
            events = await self.filter_events(earliest = dt.datetime.now(dt.timezone.utc))
        elif mode == 'all':
            events = await self.filter_events()
        matched = Schedule.find_event(events, search,-1)
        messages = Schedule.relstr_event(matched, timezone)
        for msg in messages:
            await self.bot.say(msg)
            
        
    @commands.command()
    async def next(self, search='', tz_str=''):
        default = pytz.timezone(cf.tz)
        timezone = Schedule.parse_tz(tz_str, default, cf.custom_tz)
        now = dt.datetime.now(dt.timezone.utc)
        upcoming = await self.filter_events(earliest = now)
        matched = Schedule.find_event(upcoming, search.lower(), 1)
        
        if len(matched) >= 1:
            msg = Schedule.relstr_event(matched, timezone)[0]
        else:
            msg = 'No scheduled {} found.'.format(search)

        await self.bot.say(msg)
