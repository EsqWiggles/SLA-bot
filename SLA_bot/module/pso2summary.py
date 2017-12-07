"""Count the number of each scheduled PSO2 event

Counts events from pso2calendar.py, normalizing the string to reduce the rate
of error caused by human typos of the same name in the calendar.

Attributes:
    cache: String of the counted events
"""
import asyncio
import collections
import copy
import datetime as dt
import string

import SLA_bot.config as cf
import SLA_bot.module.pso2calendar as PSO2Calendar

cache = ''
counted_events = [] #previous list of events that were counted

transtable = str.maketrans("", "", string.punctuation + string.whitespace)
def strip(s):
    """Return the string in lowercase without punctuations."""
    return s.translate(transtable).lower()

#Searching is on stripped names, so store searches as stripped too
search_alias = collections.OrderedDict()
for substring, alias in cf.section('PSO2 Summary').items():
    search_alias[strip(substring)] = alias

def read():
    """Recount the events if necesarry and return the counts as a string."""
    now = dt.datetime.now(dt.timezone.utc)
    events = [x for x in PSO2Calendar.events if x.end > now]
    if not events:
        return '`x 0` Scheduled events!'
    
    global cache
    global counted_events
    if counted_events != events or not cache:
        counted_events = copy.copy(events)
        cache = strfcount(count_events(events, search_alias)) + '\n** **'
    return cache

def strfcount(name_count):
    """Return the dictionary of events and their count as a string."""
    if not name_count:
        return ''
    lines = []
    c_width = len(str(max(name_count.values())))
    data = sorted(name_count.items(), key=lambda x: x[0])
    for name, count in data:
        lines.append('`x {:{width}d}` {}'.format(count, name, width=c_width))
    return '\n'.join(lines)

def count_events(events, aliases={}):
    """Return the count of events as a dictionary of name -> count number.
    
    Count the events by name or partially and sorting them into an alias.
    Ignore whitespace and punctuation in the event name but not in aliases.
    
        Args:
            events (list): CalendarEvents to count.
            aliases: orignal -> new name dictionary. Strip the keys.
            
        Returns:
            A dictionary with the name of the event and the number of them.
    """
    label_firstname = {}
    name_count = {}
    for e in events:
        name = e.name
        label = strip(e.name)
        if label in label_firstname:
            name_count[label_firstname[label]] += 1
        else:
            for search, alias in aliases.items():
                if search in label:
                    name = alias
                    break
            label_firstname[label] = name
            name_count.setdefault(name, 0)
            name_count[name] += 1
    return name_count
