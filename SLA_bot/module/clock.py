import datetime as dt

import SLA_bot.config as cf

hand = 0
tz = cf.gettimezone('General', 'timezone')

def update():
    global hand
    hand = hand % 12 + 1

def read():
    time = dt.datetime.now(tz).strftime('%H:%M %Z - %m/%d')
    return ':clock{}: {}'.format(hand, time)
    
