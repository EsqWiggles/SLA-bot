import asyncio
import datetime as dt

import aiohttp
import pytz

from   SLA_bot.gameevent import MultiShipEvent


async def download(url):
    async with aiohttp.get(url) as response:
        return await response.json()

def parse_event_text(text):
    events = [''] * 11
    events[0] = text
    data = text.split('\n')
    for i in range(1,11):
        ship = '{:02d}:'.format(i)
        for line in data:
            line = line.strip()
            if line.startswith(ship):
                events[i] = line[3:]
    return events

def parse_notices(notices, ref_dt):
    if notices == None or len(notices) < 1:
        return []

    parsed = []
    jst = pytz.timezone('Asia/Tokyo')
    title = 'Unscheduled Emergency Quest'
    
    base_dt = ref_dt.astimezone(jst)
    base_date = base_dt.date()
    if notices[0]['jst'] == 0 and base_dt.hour >= 22:
        base_date += dt.timedelta(days=1)

    prev_hour = 99
    for n in notices:
        hour = n['jst']
        guess_dt = dt.datetime.combine(base_date, dt.time(hour=hour))
        guess_dt = jst.localize(guess_dt)
        guess_dt = guess_dt.astimezone(dt.timezone.utc)
        events = parse_event_text(n['text'])
        
        parsed.append(MultiShipEvent(title, events, guess_dt))
        
        if prev_hour <  hour:
            base_date -= dt.timedelta(days=1)
        prev_hour = hour
    return parsed
        
