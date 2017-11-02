import asyncio
import datetime as dt
import string

import SLA_bot.module.pso2calendar as PSO2Calendar

groups = ["Arks League", "Casino Boost"]
transtable = str.maketrans("", "", string.punctuation + string.whitespace)

def read():
    events = PSO2Calendar.events
    if not events:
        return '`x 0` Scheduled events!'
    return strfevents(events) + '\n** **'

def strfevents(events):
    lines = []
    name_count = count_events(events)
    count_length = len(str(max(name_count.values())))
    data = sorted(name_count.items(), key=lambda x: x[0])
    for name, count in data:
        lines.append('`x {:{width}d}` {}'.format(count, name, width=count_length))
    return '\n'.join(lines)
    
def count_events(events):
    count = {}
    earliest_name = {}
    for e in events:
        key = e.name
        stripped = strip(key)
        for g in groups:
            if strip(g) in stripped:
                key = g
        if stripped in earliest_name:
            key = earliest_name[stripped]

        try:
            count[key] += 1
        except KeyError:
            count[key] = 1
            earliest_name[stripped] = key
    return count

def strip(s):
    return s.translate(transtable).lower()
    

    
