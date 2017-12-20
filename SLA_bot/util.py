"""Miscellaneous utiliy functions
"""

import aiohttp
import asyncio
import collections
import datetime as dt
import math
import os
import re
import sys
import traceback

known_exceptions = {}
project_dir = os.path.dirname(os.path.dirname(__file__))

GetErrors = (aiohttp.ClientConnectorError, aiohttp.ClientOSError, 
            aiohttp.ClientPayloadError, asyncio.TimeoutError)

def note(message):
    localtime = dt.datetime.now(dt.timezone.utc).astimezone()
    #localtime.isoformat(timespec=seconds)) python v3.6
    print('[{}] {}'.format(localtime.strftime('%Y-%m-%dT%H:%M:%S%z'), message))

def print_new_exceptions():
    """Print only new exceptions that this function has not processed.
    
    Use in the except block to print out the error's stack trace if it has not
    already been printed by this function already. The function is mainly used
    to ignore general or unforseen errors in the bot loop instead of halting
    the component or bot completely. In addition, it prevents the stderr or log
    file from being flooded with the same error being ignored in a loop.
    
    Note:
        Do not use this if data on the frequency of a particular error is
        desired. If the error is known, please handle it properly!
    """
    global known_exceptions
    stack_trace = str(traceback.extract_tb(sys.exc_info()[2]))
    if not stack_trace in known_exceptions:
        if len(known_exceptions) >= 1000:
            known_exceptions.clear()
        known_exceptions[stack_trace] = True
        print('---- Ignored following error: ----', file=sys.stderr)
        traceback.print_exc()
        print('--------\n', file=sys.stderr)
        
def strip_tags(tag, text):
    """Return the string inside the give tag of the HTML/XML text.
    
    Only works for elements that have a start and close tag in the format
    <example>text</example>. Ignores any attributes in the start tag.
    
    Args:
        tag (str): The name of the tag to be stripped.
        text (str): HTML or XML text to extract from.
        
    Returns:
        The string of text inside the tags.
    """
    #Lazy data extraction. If more power is needed, use html.parser instead.
    reg_exp = '<{}.*?>(.*?)</{}>'.format(tag, tag)
    matched_group = re.search(reg_exp, text, re.DOTALL).groups()
    return matched_group[0] if matched_group else ''

def two_unit_tdelta(tdelta):
    """Return the timedelta as a string with 2 units of time. 
    
    Args:
        tdelta (timedelta): A non-negative timedelta object.
        
    Returns:
        A string in the form #x ##y, where x and y are time units.
            
        The units are w (weeks), d (days), h (hours), and m (minutes). The
        largest unit that is not below 1 is chosen, followed by the unit
        immediately below it. If the largest unit is minutes, then it is
        displayed alone as #m.
        
        The second number is a rounded 2 digit number left padded by a zero.
        However if it is minutes, the ceiling is taken instead of rounding.
    """
    total_s = tdelta.total_seconds()

    week, rem_s = divmod(total_s, 60*60*24*7)
    day = round(rem_s/(60*60*24))
    if week >= 1:
        return '{}w {:02d}d'.format(int(week), day)

    day, rem_s = divmod(total_s, 60*60*24)
    hour = round(rem_s/(60*60))
    if day >=1:
        return '{}d {:02d}h'.format(int(day), hour)

    hour, rem_s = divmod(total_s, 60*60)
    minute = math.ceil(rem_s/60)
    if hour >=1:
        return '{}h {:02d}m'.format(int(hour), minute)

    return '{}m'.format(math.ceil(total_s/60))
    
def one_unit_tdelta(tdelta):
    """Return the timedelta as a string with 1 unit of time. 
    
    Args:
        tdelta (timedelta): A non-negative timedelta object.
        
    Returns:
        A string in the form #.#x or ##x where x is a time unit.
            
        The units are w (weeks), d (days), h (hours), and m (minutes). The
        largest unit that is not below 1 is chosen.
        
        The number is rounded to 2 significant digits if below 100, and rounded
        without restriction if 100 or greater. However if it is minutes, the
        the ceiling is taken instead.
    """
    total_s = tdelta.total_seconds()
    units = collections.OrderedDict()
    units['w'] = total_s/(60*60*24*7)
    units['d'] = total_s/(60*60*24)
    units['h'] = total_s/(60*60)
    units['m'] = total_s/(60)
    for unit, value in units.items():
        if value < 1:
            continue
        if units == 'm' and value >= 10:
            return '{}{}'.format(math.ceil(value), unit)
        if value < 100:
            return '{:.2g}{}'.format(value, unit)
        return '{}{}'.format(round(value), unit)
    return '{}{}'.format(math.ceil(units['m']), 'm')
