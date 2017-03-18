import datetime as dt

import SLA_bot.config as cf
class Clock:
    async def fetch():
        header = cf.get('Clock', 'header')
        now = dt.datetime.now(cf.gettimezone('General', 'timezone'))
        hand = now.hour % 12
        hand = 12 if hand == 0 else hand
        time = now.strftime('%H:%M')
        date = now.strftime('%Y-%m-%d')
        s = ":clock{}: **{}**\n:calendar_spiral: `{}`"
        return '** **\n' + header + '\n' + s.format(hand, time, date) + '\n** **'
