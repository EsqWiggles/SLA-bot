import aiohttp
import asyncio
import datetime as dt
import json

import SLA_bot.config as cf
import SLA_bot.gcalutil as GcalUtil

id = 'pso2emgquest@gmail.com'
events = []

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
    except json.decoder.JSONDecodeError:
        pass

def read():
    if not events:
        return 'No more scheduled events!'
    now = dt.datetime.now(dt.timezone.utc)
    max = cf.gettdelta('PSO2 Calendar', 'time_range')
    tzone = cf.gettimezone('General', 'timezone')
    upcoming = [x for x in events if x.start - now < max]
    schedule = GcalUtil.strfcalendar(upcoming, now, tzone)
    return schedule + '\n** **'
