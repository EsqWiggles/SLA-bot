import datetime as dt
import urllib.parse

import SLA_bot.util as ut

class CalendarEvent:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end
        
    def __eq__(self, other):
        return (self.name == other.name and self.start == other.start
               and self.end == other.end)
        
    def __hash__(self):
        return hash((self.name, self.start, self.end))
        
    def status(self, reference_time):
        z_tdelta = dt.timedelta(seconds=0)
        s_tdelta = self.start - reference_time if self.start else z_tdelta
        e_tdelta = self.end - reference_time if self.end else z_tdelta
        if s_tdelta > z_tdelta:
            return ut.two_unit_tdelta(s_tdelta)
        if e_tdelta > z_tdelta:
            return 'End ' + ut.one_unit_tdelta(e_tdelta)
        return 'Ended'
        
    def time_range(self, tz):
        if self.start and self.end:
            start = self.start.astimezone(tz).strftime('%b %d, %H:%M')
            if self.end - self.start <= dt.timedelta(hours=23):
                end = self.end.astimezone(tz).strftime('%H:%M %Z')
            else:
                end = self.end.astimezone(tz).strftime('%b %d, %H:%M %Z')
            return '{} ~ {}'.format(start, end)
        if self.start:
            return self.start.astimezone(tz).strftime('%b %d, %H:%M %Z')
        if self.end:
            return self.end.astimezone(tz).strftime('%b %d, ??:?? ~ %H:%M %Z')
        return ''
        

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
    
def statusfevents(events, reference_time):
    lines = []
    for e in events:
        status = '{:>7}'.format(e.status(reference_time))
        lines.append('`|{:^9}|` **{}**'.format(status, e.name))
    return '\n'.join(lines)

