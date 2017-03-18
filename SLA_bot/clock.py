import datetime as dt

import SLA_bot.config as cf
class Clock:
    async def fetch():
        now = dt.datetime.now(cf.gettimezone('General', 'timezone'))
        hand = now.hour % 12
        hand = 12 if hand == 0 else hand
        time = now.strftime('%H:%M %Z')
        date = now.strftime('%Y-%m-%d')
        s = ":clock{}: **{}**\n:calendar_spiral: {}\n** **"
        return s.format(hand, time, date)
