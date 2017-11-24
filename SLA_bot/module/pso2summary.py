import asyncio
import collections
import copy
import datetime as dt
import string

import SLA_bot.config as cf
import SLA_bot.module.pso2calendar as PSO2Calendar

cache = ''
counted_events = []

transtable = str.maketrans("", "", string.punctuation + string.whitespace)
def strip(s):
    return s.translate(transtable).lower()

search_alias = collections.OrderedDict()
for substring, alias in cf.section('PSO2 Summary').items():
    search_alias[strip(substring)] = alias

def read():
    now = dt.datetime.now(dt.timezone.utc)
    events = [x for x in PSO2Calendar.events if x.end > now]
    if not events:
        return '`x 0` Scheduled events!'
    
    global cache
    global counted_events
    if counted_events != events or not cache:
        counted_events = copy.copy(events)
        cache = strfcount(count_events(events)) + '\n** **'
    return cache

def strfcount(name_count):
    lines = []
    c_width = len(str(max(name_count.values())))
    data = sorted(name_count.items(), key=lambda x: x[0])
    for name, count in data:
        lines.append('`x {:{width}d}` {}'.format(count, name, width=c_width))
    return '\n'.join(lines)

def count_events(events):
    label_firstname = {}
    name_count = {}
    for e in events:
        name = e.name
        label = strip(e.name)
        if label in label_firstname:
            name_count[label_firstname[label]] += 1
        else:
            for search, alias in search_alias.items():
                if search in label:
                    name = alias
                    break
            label_firstname[label] = name
            name_count.setdefault(name, 0)
            name_count[name] += 1
    return name_count
