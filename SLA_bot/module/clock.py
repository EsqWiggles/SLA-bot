"""Simple datetime output with a semi-animated clock."""

import datetime as dt
import SLA_bot.config as cf

hand = 0
tz = cf.gettimezone('General', 'timezone')

def update():
    """Move clock hand forward by 1 hour."""
    global hand
    hand = hand % 12 + 1

def read():
    """Return string of current time and date with a clock icon."""
    time = dt.datetime.now(tz).strftime('%H:%M %Z - %m/%d')
    return ':clock{}: {}'.format(hand, time)
    
