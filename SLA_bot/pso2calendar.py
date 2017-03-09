import aiohttp
import asyncio
import collections
import datetime as dt
import math

import pytz

from   SLA_bot.gcalutil import GcalUtil

class PSO2Calendar:
    id = 'pso2emgquest@gmail.com'
    key = 'apikey'
    tz = pytz.timezone('Asia/Tokyo')
    events = []

    async def download(url):
        async with aiohttp.get(url) as response:
            return await response.json()

    async def update():
        now = dt.datetime.now(dt.timezone.utc)
        now = now.astimezone(dt.timezone.utc)
        url = GcalUtil.build_get(PSO2Calendar.id, PSO2Calendar.key, end_min = now)
        data = await PSO2Calendar.download(url)
        PSO2Calendar.events = GcalUtil.parse_data(data)
        PSO2Calendar.events.sort(key=lambda event: event.start)

    async def fetch():
        await PSO2Calendar.update()
        now = dt.datetime.now(dt.timezone.utc)
        max = dt.timedelta(hours=24)
        upcoming = [x for x in PSO2Calendar.events if x.start - now < max]
        return GcalUtil.strfcalendar(upcoming, now, PSO2Calendar.tz)