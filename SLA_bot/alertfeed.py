import asyncio
import datetime as dt
import json
import re

import aiohttp
import pytz

from   SLA_bot.gameevent import MultiShipEvent

class AlertFeed:
    source_url = 'http://pso2emq.flyergo.eu/api/v2/'

    async def download(url):
        try:
            async with aiohttp.get(url) as response:
                return await response.json()
        except json.decoder.JSONDecodeError:
            pass

    def parse_data(data):
        latest_alert = data[0]['text']
        lines = latest_alert.splitlines()
        header = '-' * len(lines[0])
        lines.insert(1, header)
        text = '\n'.join(lines)
        return '```fix\n{}\n```'.format(text)
            
    async def fetch():
        raw_data = await AlertFeed.download(AlertFeed.source_url)
        return AlertFeed.parse_data(raw_data)
        

# def parse_event_text(text):
    # events = [''] * 11
    # events[0] = text
    # data = text.split('\n')
    # for i in range(1,11):
        # ship = '{:02d}:'.format(i)
        # regex = '{}(?!\d\d)'.format(ship)
        # for line in data:
            # line = line.strip()
            # if re.match(regex, line):
                # events[i] = line[3:]
    # return events

# def parse_notices(notices, ref_dt):
    # if notices == None or len(notices) < 1:
        # return []

    # parsed = []
    # jst = pytz.timezone('Asia/Tokyo')
    # title = 'Unscheduled Emergency Quest'
    
    # base_dt = ref_dt.astimezone(jst)
    # base_date = base_dt.date()
    # if notices[0]['jst'] == 0 and base_dt.hour >= 22:
        # base_date += dt.timedelta(days=1)

    # prev_hour = 99
    # for n in notices:
        # hour = n['jst']
        # guess_dt = dt.datetime.combine(base_date, dt.time(hour=hour))
        # guess_dt = jst.localize(guess_dt)
        # guess_dt = guess_dt.astimezone(dt.timezone.utc)
        # events = parse_event_text(n['text'])
        
        # parsed.append(MultiShipEvent(title, events, guess_dt))
        
        # if prev_hour <  hour:
            # base_date -= dt.timedelta(days=1)
        # prev_hour = hour
    # return parsed
        
