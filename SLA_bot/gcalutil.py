import datetime as dt
import urllib.parse

import SLA_bot.util as ut

class CalendarEvent:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

def gtimefdt(date_time):
    return dt.datetime.strftime(date_time, '%Y-%m-%dT%H:%M:%SZ')
    
def gtimepdt(time_string):
    naive = dt.datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%SZ')
    return naive.replace(tzinfo=dt.timezone.utc)

def parse_data(json_data):
    events = []
    for item in json_data['items']:
        n = item['summary']
        s = gtimepdt(item['start']['dateTime'])
        e = gtimepdt(item['end']['dateTime'])
        new_event = CalendarEvent(n, s, e)
        events.append(new_event)
    return events

def build_get(cal_id, key, end_min=None, start_max=None):
    query = {}
    query['maxResults'] = '2500'
    query['timeZone'] = 'UTC'
    query['key'] = key
    if end_min:
        query['timeMin'] = gtimefdt(end_min)
    if start_max:
        query['timeMax'] = gtimefdt(start_max)

    url = 'https://www.googleapis.com/calendar/v3/calendars/{}/events?'
    params = urllib.parse.urlencode(query)
    return url.format(urllib.parse.quote_plus(cal_id)) + params

def strfcalendar(events, reference_time, time_zone):
    lines = []
    for event in events:
        s_tdelta = event.start - reference_time
        e_tdelta = event.end - reference_time
        if s_tdelta > dt.timedelta(seconds=0):
            status = ut.two_unit_tdelta(s_tdelta)
        elif e_tdelta > dt.timedelta(seconds=0):
            status = 'End ' + ut.one_unit_tdelta(e_tdelta)
        else:
            status = 'Ended'
        status = '{:>7}'.format(status)
        
        s = event.start.astimezone(time_zone).strftime('%H:%M')
        e = event.end.astimezone(time_zone).strftime('%H:%M')
        n = event.name
        l = '`|{:^9}|`  `{} ~ {}`  **{}**'.format(status, s, e, n)
        lines.append(l)
    return '\n'.join(lines)
