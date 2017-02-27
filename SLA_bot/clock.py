import datetime as dt

from   SLA_bot.config import Config as cf

class Clock:
    async def fetch():
        now = dt.datetime.now(cf.tz)
        hand = now.hour % 12
        hand = 12 if hand == 0 else hand
        time = now.strftime('%H:%M %Z')
        date = now.strftime('%Y-%m-%d')
        s = ":clock{}: **{}**\n:calendar_spiral: {}\n** **"
        return s.format(hand, time, date)
