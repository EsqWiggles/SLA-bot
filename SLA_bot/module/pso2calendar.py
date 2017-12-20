"""List PSO2 event schedule

Download, store, and list PSO2's schedule. Update at least once before reading.

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
import SLA_bot.util as ut

events = []

api_key = cf.get('General', 'google_api_key')
id = 'pso2emgquest@gmail.com' #id of the google calendar, not the whole URL
time_range = cf.gettdelta('PSO2 Calendar', 'time_range')
tz = cf.gettimezone('General', 'timezone')

async def update():
    """Download, parse, and store the data as CalendarEvent objects."""
    global events
    events = GcalUtil.parse_data(await download(id))
    events.sort(key=lambda event: event.start)

async def download(cal_id):
    """Return json data of events that start or end between now and 14 days."""
    #Almost all schedules span 1~2 week, but add a max to avoid human errors.
    now = dt.datetime.now(dt.timezone.utc)
    max = now + dt.timedelta(days=14)
    url = GcalUtil.build_get(cal_id, api_key, now, max)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                    return await response.json()
    except ut.GetErrors as e:
        ut.note('Failed to GET: ' + url)
    except json.decoder.JSONDecodeError:
        ut.note('Unexpected data format from: ' + url)
        return {}

def read():
    """Return the list of events that have not started or ended as a string."""
    if not events:
        return 'No more scheduled events!'
    now = dt.datetime.now(dt.timezone.utc)
    upcoming = [x for x in events if x.start - now < time_range]
    return GcalUtil.statusfevents(upcoming, now) + '\n** **'
