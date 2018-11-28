"""Collect hourly event announcements for PSO2

Take announcement data from a third party source, convert it into a string,
and store it for later reads. Update at least once before reading.
"""

# The current source is already translated into English. In the event that the
# flyergo source is discontinued, this module must adapt to a new source. If no
# other alternatives can be found, then this will fall back to using twitter
# bot at https://twitter.com/pso2_emg_hour and translating it.

import aiohttp
import asyncio
import json
import re

import SLA_bot.util as ut

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
    except ut.GetErrors as e:
        ut.note('Failed to GET: ' + source_url)
    except (json.decoder.JSONDecodeError, IndexError, KeyError) as e:
        ut.note('Unexpected data format from: ' + source_url)

def read():
    """Return the string of the most recent announcement."""
    if not cache:
        return '[ ?? JST Emergency Quest Notice ]\nNot found.'
    if is_unscheduled():
        return align_shiplabels(cache) + '\n** **'
    return cache + '\n** **'

def is_unscheduled():
    """Return whether the last announcement looks like an unscheduled event."""
    # Checks if 50% or more of the lines (-1 from the header) start with what
    # looks like a ship label.
    #    Unscheduled Ship label = ##:Event Name
    #    Scheduled Time = ##:## Event Name
    # The regex matches if there are 2 numbers and a semicolon at the start of
    # the line but not if 2 more numbers and a space follows it. In case an
    # event name is added that starts with 2 digits and a space in the future,
    # exclude the common minute times of 00 and 30 instead.
    if not cache:
        return True
    ship_labels = re.findall('^\d\d:(?!\d\d\s)', cache, flags=re.MULTILINE)
    return len(ship_labels) / cache.count('\n') >= 0.50

def align_shiplabels(text):
    """Return the announcement with the ship labels aligned."""
    # See comment in is_unscheduled() for a description of the regex,
    def monospace(matched):
        return '`{}`'.format(matched.group(0))
    return re.sub('^\d\d:(?!\d\d\s)', monospace, text, flags=re.MULTILINE)


