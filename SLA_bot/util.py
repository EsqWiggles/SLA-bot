import datetime as dt

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
    
def parse_md(md_str, tz):
    y = dt.datetime.now(tz).year
    date = '{}/{}'.format(y, md_str)
    
    curr = dt.datetime.strptime(date, '%Y/%m/%d')
    if hasattr(tz, 'localize'):
        curr = tz.localize(curr)
    else:
        curr = curr.replace(tzinfo=tz)

    guess_dt = []
    if curr.year > dt.MINYEAR:
        prev = curr.replace(year=curr.year-1)
        guess_dt.append(day(prev, 0, tz))
    guess_dt.append(day(curr, 0, tz))
    if curr.year < dt.MAXYEAR:
        next = curr.replace(year=curr.year+1)
        guess_dt.append(day(next, 0, tz))
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