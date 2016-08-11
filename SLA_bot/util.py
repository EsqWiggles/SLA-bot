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