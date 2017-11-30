"""List PSO2es event schedule

Download, store, and list the mobile app's event schedule. Update at least once
before reading.

Attributes:
    events: List of CalendarEvents from last update() call. This may still
        contain events that have already ended.
"""

import aiohttp
import asyncio
import datetime as dt
import json

import SLA_bot.config as cf
import SLA_bot.gcalutil as GcalUtil

events = []

api_key = cf.get('General', 'google_api_key')
id = '1ilqbcbvl8h6g8q537220ooif4@group.calendar.google.com'
time_range = cf.gettdelta('PSO2es Calendar', 'time_range')
tz = cf.gettimezone('General', 'timezone')

async def download():
    """Return json data of events that start or end between now and 14 days."""
    #Almost all schedules span 1~2 week, but add a max to avoid human errors.
    now = dt.datetime.now(dt.timezone.utc)
    max = now + dt.timedelta(days=14)
    url = GcalUtil.build_get(id, api_key, now, max)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
    
async def update():
    """Calls download(), parses the data, and stores it in events."""
    try:
        data = await download()
        global events
        events = GcalUtil.parse_data(data)
        events.sort(key=lambda event: event.start)
    except json.decoder.JSONDecodeError:
        pass

def read():
    """Return the list of events that have not started or ended as a string."""
    if not events:
        return 'No more scheduled events!'
    now = dt.datetime.now(dt.timezone.utc)
    upcoming = [x for x in events if x.start - now < time_range]
    return GcalUtil.statusfevents(upcoming, now) + '\n** **'


