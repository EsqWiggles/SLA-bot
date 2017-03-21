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

    def count_events():
        count = {}
        earliest_name = {}
        for e in PSO2Calendar.events:
            key = e.name
            lower = e.name.lower()
            for g in PSO2Calendar.groups:
                if g.lower() in lower:
                    key = g
            if lower in earliest_name:
                key = earliest_name[lower]

            try:
                count[key] += 1
            except KeyError:
                count[key] = 1
                earliest_name[lower] = key
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
        header = cf.get('PSO2 Calendar', 'header')
        await PSO2Calendar.update()
        if not PSO2Calendar.events:
            return '** **\n' + header + '\n\n' + 'No more scheduled events!' + '\n** **'
        now = dt.datetime.now(dt.timezone.utc)
        max = cf.gettdelta('PSO2 Calendar', 'time_range')
        tzone = cf.gettimezone('General', 'timezone')
        upcoming = [x for x in PSO2Calendar.events if x.start - now < max]
        schedule = GcalUtil.strfcalendar(upcoming, now, tzone)
        summary = PSO2Calendar.strfcount()
        return '** **\n' + header + '\n\n' + schedule + '\n\n' + summary + '\n** **'