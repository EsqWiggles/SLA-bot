import asyncio
import datetime as dt
import math
import os
import sys

import aiohttp
from   discord.ext import commands
import icalendar as ical
import pytz

from SLA_bot.config import Config as cf

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
            
    def parse_tz(tz_str, custom=None):
        if custom != None:
            custom_tz = tz_str.lower()
            if custom_tz in custom:
                return custom[custom_tz]
                
        country_code = tz_str.upper()
        if country_code in pytz.country_timezones:
            return pytz.country_timezones[country_code][0]

        try:
            pytz.timezone(tz_str)
            return tz_str
        except pytz.exceptions.UnknownTimeZoneError:
            return None

        return None
    
    async def event_print(self, start=None, end=None, tz=None):
        if tz == None:
            tz = pytz.timezone(cf.tz)

        prev_date = None
        msg_chunk = None

        for e in reversed(self._events):
            start_time = e.get('dtstart').dt.astimezone(tz)
            if start != None and start_time < start:
                continue
            if end != None and start_time > end :
                continue

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
    
    @commands.command()
    async def eq_print(self, tz_str=None):
        timezone = None
        if tz_str != None:
            parsed = Schedule.parse_tz(tz_str, cf.custom_tz)
            if parsed == None:
                return
            timezone = pytz.timezone(parsed)
        await self.event_print(start=dt.datetime.now(tz=dt.timezone.utc), tz=timezone)

        
