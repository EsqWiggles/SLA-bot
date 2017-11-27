"""Collect hourly event announcements for PSO2

Take announcement data from a third party source, convert it into a string,
and store it for later reads. Update at least once before reading.
"""

# The current source is already translated into English. In the event that the
# flyergo source is discontinued, this module must adapt to a new source. If no
# other alternatives can be found, then this will fall back to using twitter
# bot at https://twitter.com/pso2_emg_hour and translating it.

import asyncio
import json
import re

import aiohttp

cache = ''
source_url = 'http://pso2emq.flyergo.eu/api/v2/'

async def update():
    """Download and store the announcement data."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(source_url) as response:
                global cache
                data = await response.json(content_type=None)
                cache = data[0]['text']
    except (json.decoder.JSONDecodeError, IndexError, KeyError) as e:
        pass

def read():
    """Return the string of the most recent announcement."""
    if not cache:
        return '[ ?? JST Emergency Quest Notice ]\nNot found.'
    if is_unscheduled():
        return align_shiplabels(cache) + '\n** **'
    return cache + '\n** **'

def is_unscheduled():
    """Return whether the last announcement looks like an unscheduled event."""
    # Unscheduled events typically list each ship number from 01: through 10:
    # but sometimes does a partial list so this only checks for 3+ ship labels.
    # The regex matches if there are 2 numbers and a semicolon at the start of
    # the line but not if 2 more numbers and a space follows it, since that is
    # most likely a time label, like 13:00 Event Name, instead of a ship label.
    if not cache:
        return True
    return len(re.findall('^\d\d:(?!\d\d\s)', cache, flags=re.MULTILINE)) >= 3

def align_shiplabels(text):
    """Return the announcement with the ship labels aligned."""
    # See comment in is_unscheduled() for a description of the regex,
    def monospace(matched):
        return '`{}`'.format(matched.group(0))
    return re.sub('^\d\d:(?!\d\d\s)', monospace, text, flags=re.MULTILINE)


