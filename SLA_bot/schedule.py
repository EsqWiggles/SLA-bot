import asyncio
import datetime as dt
import math
import os
import sys

import aiohttp
from   discord.ext import commands
import icalendar as ical
import pytz

import SLA_bot.config as cf

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
        current_events.sort(key=lambda event: event.get('dtstart').dt, reverse=True)
        self._events = current_events
        
        
    @commands.command()
    async def eq_print(self):
        jst = pytz.timezone('Asia/Tokyo')
        msg = ''
        for event in self._events:
            name = event.get('summary')
            start_time = event.get('dtstart').dt.astimezone(jst)
            relative_time = math.ceil((start_time - dt.datetime.now(dt.timezone.utc)).total_seconds()/60)
            msg += ('{0:36} | {1:4}m | {2}\n'.format(name, relative_time, start_time))
        await self.bot.say('```{}```'.format(msg))
 
        
