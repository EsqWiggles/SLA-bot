import asyncio
import collections
import datetime as dt
import string

import SLA_bot.config as cf
import SLA_bot.module.pso2calendar as PSO2Calendar


transtable = str.maketrans("", "", string.punctuation + string.whitespace)
def strip(s):
    return s.translate(transtable).lower()
    
search_alias = collections.OrderedDict()
for substring, alias in cf.section('PSO2 Summary').items():
    search_alias[strip(substring)] = alias
name_countlabel = {}

class Counter:
    def __init__(self, name, count):
        self.name = name
        self.count = count

def read():
    events = PSO2Calendar.events
    if not events:
        return '`x 0` Scheduled events!'
    return strfevents(events) + '\n** **'

def strfevents(events):
    lines = []
    counters = list(count_events(events).values())
    count_length = len(str(max( [x.count for x in counters] )))
    data = sorted(counters, key=lambda x: x.name)
    for c in data:
        lines.append('`x {:{width}d}` {}'.format(c.count, c.name, width=count_length))
    return '\n'.join(lines)

def count_events(events):
    count = {}
    for e in events:
        name = e.name
        label = find_label(name)
        if label in count:
            count[label].count += 1
        else:
            counter_name = name
            for alias in search_alias.values():
                if label == strip(alias):
                    counter_name = alias
            count[label] = Counter(counter_name, 1)
    return count
    
def find_label(name):
    global name_countlabel
    if name in name_countlabel:
        return name_countlabel[name]
    stripped = strip(name)
    for search, alias in search_alias.items():
        if search in stripped:
            name_countlabel[name] = strip(alias)
            return name_countlabel[name]
    name_countlabel[name] = stripped
    return stripped
