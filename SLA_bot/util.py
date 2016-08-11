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