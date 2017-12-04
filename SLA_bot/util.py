"""Miscellaneous utiliy functions
"""

import collections
import os
import re
import sys
import traceback

known_exceptions = {}
project_dir = os.path.dirname(os.path.dirname(__file__))
 
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
    stack_trace = str(traceback.extract_tb(sys.exc_info()[2]))
    if not stack_trace in known_exceptions:
        #todo:clear dictionary at some length to avoid hogging memory
        known_exceptions[stack_trace] = True
        traceback.print_exc()
        
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
        A string in the form ##x ##y, where x and y are time units.
            
        The units are w (weeks), d (days), h (hours), and m (minutes). The
        largest unit that is not below 1 is chosen, followed by the unit
        immediately below it. If the largest unit is minutes, then it is
        displayed alone as ##m.
        
        The numbers are 2 digits, left padded by a zero with two exceptions.
        If the weeks are greater than 99, it will extend beyond 2 digits. If
        it is only minutes, it will not be padded by a zero.
    """
    #todo: replace rounding, looks off by 30s with clocks
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
    minute = round(rem_s/60)
    if hour >=1:
        return '{}h {:02d}m'.format(int(hour), minute)

    return '{}m'.format(round(total_s/60))
    
def one_unit_tdelta(tdelta):
    """Return the timedelta as a string with 1 unit of time. 
    
    Args:
        tdelta (timedelta): A non-negative timedelta object.
        
    Returns:
        A string in the form #.#x or ##x where x is a time unit.
            
        The units are w (weeks), d (days), h (hours), and m (minutes). The
        largest unit that is not below 1 is chosen.
        
        The number is rounded to 2 significant digits if it below 100, and
        rounded without restriction if it is 100 or greater. Any value 0 or
        below is returned as 0m.
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
        if value < 100:
            return '{:.2g}{}'.format(value, unit)
        return '{}{}'.format(round(value), unit)
    return '0m'
