import aiohttp
import asyncio
import datetime as dt
import json
import string

import SLA_bot.config as cf
import SLA_bot.gcalutil as GcalUtil

id = 'pso2emgquest@gmail.com'
events = []
counter = {}
groups = ["Arks League", "Casino Boost"]
transtable = str.maketrans("", "", string.punctuation + string.whitespace)

async def download():
    now = dt.datetime.now(dt.timezone.utc)
    max = now + dt.timedelta(days=14)
    api_key = cf.get('General', 'google_api_key')
    url = GcalUtil.build_get(id, api_key, now, max)
    async with aiohttp.get(url) as response:
        return await response.json()
        
async def update():
    try:
        data = await download()
        global events
        events = GcalUtil.parse_data(data)
        events.sort(key=lambda event: event.start)
        global counter
        counter = count_events()
    except json.decoder.JSONDecodeError:
        pass

def count_events():
    count = {}
    earliest_name = {}
    for e in events:
        key = e.name
        stripped = strip(key)
        for g in groups:
            if strip(g) in stripped:
                key = g
        if stripped in earliest_name:
            key = earliest_name[stripped]

        try:
            count[key] += 1
        except KeyError:
            count[key] = 1
            earliest_name[stripped] = key
    return count

def strip(s):
    return s.translate(transtable).lower()
    
def strfcount():
    lines = []
    data = sorted(counter.items(), key=lambda x: x[0])
    for name, count in data:
        lines.append('`x{:>3}` {}'.format(count, name))
    return '\n'.join(lines)
    
async def read():
    await update()
    header = cf.get('PSO2 Calendar', 'header')
    if not events:
        return 'No more scheduled events!'
    now = dt.datetime.now(dt.timezone.utc)
    max = cf.gettdelta('PSO2 Calendar', 'time_range')
    tzone = cf.gettimezone('General', 'timezone')
    upcoming = [x for x in events if x.start - now < max]
    schedule = GcalUtil.strfcalendar(upcoming, now, tzone)
    summary = strfcount()
    return schedule + '\n\n' + summary + '\n** **'
