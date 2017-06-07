import collections
import os
import traceback
import sys

project_dir = os.path.dirname(os.path.dirname(__file__))

async def try_ignore_errors(func, *args, **kwargs):
    try:
        await func(*args, **kwargs)
    except Exception as e:
        traceback_stack = traceback.extract_tb(sys.exc_info()[2])
        stack_index = -1
        for i, error_data in enumerate(traceback_stack):
            parent_dir = os.path.dirname(os.path.dirname(error_data[0]))
            if parent_dir == project_dir:
                stack_index = i
        file, line, _, _ = traceback_stack[stack_index]
        print('Ignored Error from: File "{}", line {}'.format(file, line))
        print('{}: {}\n'.format(type(e).__name__, e))

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
