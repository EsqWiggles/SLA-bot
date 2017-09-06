import collections
import os
import sys
import traceback

known_exceptions = {}
project_dir = os.path.dirname(os.path.dirname(__file__))
 
def print_new_exceptions():
    stack_trace = str(traceback.extract_tb(sys.exc_info()[2]))
    if not stack_trace in known_exceptions:
        known_exceptions[stack_trace] = True
        traceback.print_exc()

def two_unit_tdelta(tdelta):
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
