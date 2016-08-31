import asyncio
import datetime as dt

import pytz

def day(base_dt, offset=0, tz=None):
    if tz == None:
        tz = pytz.utc
    new_date = base_dt.astimezone(tz).date() + dt.timedelta(days=offset)
    y = new_date.year
    m = new_date.month
    d = new_date.day
    local_dt = dt.datetime(y, m, d, 0, 0, 0, 0)
    if hasattr(tz, 'localize'):
        local_dt = tz.localize(local_dt)
    else:
        local_dt = local_dt.replace(tzinfo=tz)
    return local_dt.astimezone(dt.timezone.utc)

def guess_year(some_date, tz):
    y = dt.datetime.now(tz).year
    m = some_date.month
    d = some_date.day
    guess_dates = []
    for offset in range(-1, 2):
        try: 
            new_date = dt.date(y+offset, m, d)
        except ValueError:
            continue
        guess_dates.append(new_date)
    return guess_dates

def guess_month(some_date, tz):
    y = some_date.year
    m = dt.datetime.now(tz).month
    d = some_date.day
    guess_dates = []
    for offset in range(-1, 2):
        new_m = ((m+offset-1)%12)+1
        try: 
            new_date = dt.date(y, new_m, d)
        except ValueError:
            continue
        guess_dates.append(new_date)
    return guess_dates

def parse_date(date_str, tz):
    now = dt.datetime.now(tz)
    y, m, d = '', '', ''
    try:
        y, m, d = date_str.split('/')
    except ValueError:
        try:
            m, d = date_str.split('/')
        except ValueError:
            d = date_str
            
    yr = int(y or now.year)
    mn = int(m or now.month)
    dy = int(d or now.day)
    base_date = dt.date(yr, mn, dy)
    
    guess = [base_date]
    if(m == '' and date_str != ''):
        guess = guess_month(base_date, tz)
        
    if(y == '' and date_str != ''):
        months = guess
        guess = []
        for m in months:
            guess.extend(guess_year(m, tz))
            
    guess_dt = []
    for g in guess:
        new_dt = dt.datetime(g.year, g.month, g.day)
        if hasattr(tz, 'localize'):
            new_dt = tz.localize(new_dt)
        else:
            new_dt = new_dt.replace(tzinfo=tz)
        guess_dt.append(new_dt)
    guess_dt.sort()
    return guess_dt
    
def unitsfdelta(tdelta):
    total_s = int(tdelta.total_seconds())
    day, remain_s = divmod(total_s, 24*60*60)
    hour, remain_s = divmod(remain_s, 60*60)
    min, sec = divmod(remain_s, 60)
    return day, hour, min, sec
    
    
def strfdelta(tdelta, unit_str = ('days', 'hr', 'min', 'sec')):
    units = unitsfdelta(tdelta)
    last = len(units) - 1
    for i in range(0, len(units)):
        if units[i] == 0 and i != last:
            continue
        
        parts = ['{}{}'.format(units[i], unit_str[i])]
        if i < last and units[i+1] != 0:
            parts.append('{}{}'.format(units[i+1], unit_str[i+1]))
        return ' '.join(parts)
        
        
def prev_weekday(weekday, at):
    curr = dt.datetime.now(dt.timezone.utc)
    prev = curr.replace(hour=at.hour, minute=at.minute,
                        second=at.second, microsecond=0)
    while(prev >= curr or prev.isoweekday() != weekday):
        prev = prev - dt.timedelta(days=1)
    return prev
    
def utctz_offset(offset):
    h,sep,m = offset.partition(':')
    h = int(h)
    sign = 1
    if h < 0:
        sign = -1
    if m == '':
        m = 0
    else:
        m = int(m)
    m = sign * m
    utc_tz = dt.timezone(dt.timedelta(hours=h, minutes=m))
    return utc_tz
        
def parse_tz(tz_str, default_tz=None, custom=None):
    if tz_str == None or tz_str == '':
        return default_tz
    
    try:
        return utctz_offset(tz_str)
    except ValueError:
        pass

    if custom != None:
        custom_tz = tz_str.lower()
        if custom_tz in custom:
            return pytz.timezone(custom[custom_tz])
            
    country_code = tz_str.upper()
    if country_code in pytz.country_timezones:
        return pytz.timezone(pytz.country_timezones[country_code][0])

    try:
        return pytz.timezone(tz_str)
    except pytz.exceptions.UnknownTimeZoneError:
        return None

    return None

    
def line_count(message):
    if type(message) is str:
        return 1 + message.count('\n')
    
    count = 0
    for m in message:
        count += line_count(m)
    return count


async def quiet_say(bot, message, max):
    send_method = bot.say
    if line_count(message) > max:
        send_method = bot.whisper
        
    async def recur_say(msg):
        if type(msg) is str:
            await send_method(msg)
            return

        for m in msg:
            await recur_say(m)
            
    await recur_say(message)


