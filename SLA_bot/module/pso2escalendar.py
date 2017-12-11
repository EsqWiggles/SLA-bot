"""List PSO2es event schedule

Download, store, and list the mobile app's event schedule. Update at least once
before reading.

Attributes:
    events: List of CalendarEvents from last update() call. This may still
        contain events that have already ended.
"""
#Can make a class for this and pso2calendar.py but for now leave them as
#separate files to be consistent with the rest of the bot modules.

import asyncio
import datetime as dt

import SLA_bot.config as cf
import SLA_bot.gcalutil as GcalUtil
import SLA_bot.module.pso2calendar as PSO2Calendar

events = []

id = '1ilqbcbvl8h6g8q537220ooif4@group.calendar.google.com'
time_range = cf.gettdelta('PSO2es Calendar', 'time_range')
    
async def update():
    """Download, parse, and store the data as CalendarEvent objects."""
    global events
    events = GcalUtil.parse_data(await PSO2Calendar.download(id))
    events.sort(key=lambda event: event.start)

def read():
    """Return the list of events that have not started or ended as a string."""
    if not events:
        return 'No more scheduled events!'
    now = dt.datetime.now(dt.timezone.utc)
    upcoming = [x for x in events if x.start - now < time_range]
    return GcalUtil.statusfevents(upcoming, now) + '\n** **'


