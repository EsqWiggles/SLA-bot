import aiohttp
import asyncio
import datetime as dt

import SLA_bot.config as cf
import SLA_bot.gcalutil as GcalUtil

id = '1ilqbcbvl8h6g8q537220ooif4@group.calendar.google.com'
events = []

async def download(url):
    async with aiohttp.get(url) as response:
        return await response.json()
    
async def update():
    now = dt.datetime.now(dt.timezone.utc)
    max = now + dt.timedelta(days=14)
    api_key = cf.get('General', 'google_api_key')
    url = GcalUtil.build_get(id, api_key, now, max)
    data = await download(url)
    global events
    events = GcalUtil.parse_data(data)
    events.sort(key=lambda event: event.start)

async def fetch():
    header = cf.get('PSO2es Calendar', 'header')
    await update()
    if not events:
        return '** **\n' + header + '\n\n' + 'No more scheduled events!' + '\n** **'
    now = dt.datetime.now(dt.timezone.utc)
    max = cf.gettdelta('PSO2es Calendar', 'time_range')
    tzone = cf.gettimezone('General', 'timezone')
    upcoming = [x for x in events if x.start - now < max]
    schedule = GcalUtil.strfcalendar(upcoming, now, tzone)
    return '** **\n' + header + '\n\n' + schedule + '\n** **'