import collections
import datetime as dt
import urllib.parse

class GcalUtil:
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
            s = GcalUtil.gtimepdt(item['start']['dateTime'])
            e = GcalUtil.gtimepdt(item['end']['dateTime'])
            new_event = GcalUtil.CalendarEvent(n, s, e)
            events.append(new_event)
        return events

    def build_get(cal_id, key, end_min=None, start_max=None):
        query = {}
        query['maxResults'] = '2500'
        query['timeZone'] = 'UTC'
        query['key'] = key
        if end_min:
            query['timeMin'] = GcalUtil.gtimefdt(end_min)
        if start_max:
            query['timeMax'] = GcalUtil.gtimefdt(start_max)

        
        url = 'https://www.googleapis.com/calendar/v3/calendars/{}/events?'
        params = urllib.parse.urlencode(query)
        return url.format(urllib.parse.quote_plus(cal_id)) + params
        
    def hour_minute(tdelta):
        total_m = round(tdelta.total_seconds()/60)
        hour, minute = divmod(total_m, 60)
        h = '{:>2}h'.format(hour) if hour > 0 else '{:>3}'.format('')
        return '{} {:02d}m'.format(h, minute)
        
    def single_unit(tdelta):
        total_s = tdelta.total_seconds()
        units = collections.OrderedDict()
        units['d'] = total_s/(24*60*60)
        units['h'] = total_s/(60*60)
        units['m'] = total_s/(60)
        for unit, value in units.items():
            if value < 1:
                continue
            if value < 100:
                return '{:.2g}{}'.format(value, unit)
            return '{}{}'.format(round(value), unit)
        return '0m'
        
    def strfcalendar(events, reference_time, time_zone):
        lines = []
        for event in events:
            s_tdelta = event.start - reference_time
            e_tdelta = event.end - reference_time
            if s_tdelta > dt.timedelta(seconds=0):
                status = GcalUtil.hour_minute(s_tdelta)
            elif e_tdelta > dt.timedelta(seconds=0):
                status = 'End {:>3}'.format(GcalUtil.single_unit(e_tdelta))
            else:
                status = 'Ended'
            
            s = event.start.astimezone(time_zone).strftime('%H:%M')
            e = event.end.astimezone(time_zone).strftime('%H:%M %Z')
            n = event.name
            l = '`|{:^9}|`  `{} ~ {}`  **{}**'.format(status, s, e, n)
            lines.append(l)
        return '\n'.join(lines)
