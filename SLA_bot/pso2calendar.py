import aiohttp
import asyncio
import datetime as dt

import SLA_bot.config as cf
import SLA_bot.gcalutil as GcalUtil

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
    for e in events:
        key = e.name
        lower = e.name.lower()
        for g in groups:
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
    data = sorted(counter.items(), key=lambda x: x[0])
    for name, count in data:
        lines.append('`x{:>3}` {}'.format(count, name))
    return '\n'.join(lines)
    
        
async def update():
    now = dt.datetime.now(dt.timezone.utc)
    max = now + dt.timedelta(days=14)
    api_key = cf.get('General', 'google_api_key')
    url = GcalUtil.build_get(id, api_key, now, max)
    data = await download(url)
    events = GcalUtil.parse_data(data)
    events.sort(key=lambda event: event.start)
    counter = count_events()
        

async def fetch():
    header = cf.get('PSO2 Calendar', 'header')
    await update()
    if not events:
        return '** **\n' + header + '\n\n' + 'No more scheduled events!' + '\n** **'
    now = dt.datetime.now(dt.timezone.utc)
    max = cf.gettdelta('PSO2 Calendar', 'time_range')
    tzone = cf.gettimezone('General', 'timezone')
    upcoming = [x for x in events if x.start - now < max]
    schedule = GcalUtil.strfcalendar(upcoming, now, tzone)
    summary = strfcount()
    return '** **\n' + header + '\n\n' + schedule + '\n\n' + summary + '\n** **'
