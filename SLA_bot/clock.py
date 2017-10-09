import datetime as dt

import SLA_bot.config as cf

hand = 0

def update():
    global hand
    hand = hand % 12 + 1

def read():
    tz = cf.gettimezone('General', 'timezone')
    time = dt.datetime.now(tz).strftime('%H:%M %Z - %m/%d')
    return ':clock{}: {}'.format(hand, time)
    
