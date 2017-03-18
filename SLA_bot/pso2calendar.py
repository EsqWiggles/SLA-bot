import aiohttp
import asyncio
import collections
import datetime as dt
import math

import SLA_bot.config as cf
from   SLA_bot.gcalutil import GcalUtil

class PSO2Calendar:
    id = 'pso2emgquest@gmail.com'
    events = []
    counter = {}
    groups = ["Arks League", "Casino Boost"]
    
    async def download(url):
        async with aiohttp.get(url) as response:
            return await response.json()

            #make case insensitive
    def count_events():
        count = {}
        for e in PSO2Calendar.events:
            key = e.name
            for g in PSO2Calendar.groups:
                if g in key:
                    key = g
            try:
                count[key] += 1
            except KeyError:
                count[key] = 1
        return count
        
    def strfcount():
        lines = []
        data = sorted(PSO2Calendar.counter.items(), key=lambda x: x[0])
        for name, count in data:
            lines.append('`x{:>3}` {}'.format(count, name))
        return '\n'.join(lines)
        
            
    async def update():
        now = dt.datetime.now(dt.timezone.utc)
        max = now + dt.timedelta(days=14)
        api_key = cf.get('General', 'google_api_key')
        url = GcalUtil.build_get(PSO2Calendar.id, api_key, now, max)
        data = await PSO2Calendar.download(url)
        PSO2Calendar.events = GcalUtil.parse_data(data)
        PSO2Calendar.events.sort(key=lambda event: event.start)
        PSO2Calendar.counter = PSO2Calendar.count_events()
            

    async def fetch():
        await PSO2Calendar.update()
        now = dt.datetime.now(dt.timezone.utc)
        max = dt.timedelta(hours=24)
        tzone = cf.gettimezone('General', 'timezone')
        upcoming = [x for x in PSO2Calendar.events if x.start - now < max]
        schedule = GcalUtil.strfcalendar(upcoming, now, tzone)
        summary = PSO2Calendar.strfcount()
        return schedule + '\n\n' + summary