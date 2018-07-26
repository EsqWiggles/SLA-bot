"""Helper for Google Calendar API

Perform basic retrieval and parsing of Google Calendar events into
CalendarEvent classes.
"""
#If more support is needed for the API, use official py package instead

import datetime as dt
import urllib.parse

import SLA_bot.util as ut

class CalendarEvent:
    """Container for basic information in a scheduled event.
    
    Attributes:
        name (str): Name of the event
        start (datetime): Start date and time of the event
        end (datetime): End date and time of the event
    """
    
    def __init__(self, name, start, end):
        """Return a CalendarEvent with the given name, start and end time.
        
        Args:
            name (str): Name of the event
            start (datetime): Start date and time of the event
            end (datetime): End date and time of the event
        """
        self.name = name
        self.start = start
        self.end = end
        
    def __eq__(self, other):
        return (self.name == other.name and self.start == other.start
               and self.end == other.end)
        
    def __hash__(self):
        return hash((self.name, self.start, self.end))
        
    def status(self, reference_time):
        """Return when the event will start, end, or if it already ended.
        
        Args:
            reference_time (datetime): Whether the event will start, end, or
                has ended at the given time. Often the current time is used.
        
        Returns:
            string: Three different kind of strings depending on the time.
            
            If not started, return the time until the event will start in the
                form "##h ##m" (hours, minutes) up to "##w ##d" (weeks, days).
                
            If started but not ended, return the time until the event ends in
                the form "End ##m" (minutes) up to "End ##w" (weeks).
                
            If the event has ended or the event is missing the start or end
                attribute, return "Ended".
        """
        z_tdelta = dt.timedelta(seconds=0)
        s_tdelta = self.start - reference_time if self.start else z_tdelta
        e_tdelta = self.end - reference_time if self.end else z_tdelta
        if s_tdelta > z_tdelta:
            return ut.two_unit_tdelta(s_tdelta)
        if e_tdelta > z_tdelta:
            return 'End ' + ut.one_unit_tdelta(e_tdelta)
        return 'Ended'
        
    def time_range(self, tz):
        """Return a string of the start time to the end time.
        
        Args:
            tz (timezone): timezone used to localize the start and end time.
            
        Returns:
            string: Month Day, Start(hour:minute) ~ End(hour:minute) Timezone
            
            If the start and end time are more than 23 hours apart, the string
                will include the month and date for the end time as well.
                
            If the start or end time are not set, they will be omitted.
            
            If neither times are set, return the empty string.
        """
        if self.start and self.end:
            start = self.start.astimezone(tz).strftime('%b %d, %H:%M')
            #While events lasting 24 hours or more cannot be written clearly
            #without the date, events lasting 23 hours can but also feel like
            #typos. For example, 13:00 ~ 12:30 can seem more likely to be a
            #typo for 13:00 ~ 13:30 than lasting 23 hours and 30 minutes.
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
    """Return a string in the API's time format from a datetime."""
    return date_time.isoformat()
    
def gtimepdt(time_string):
    """Return a UTC datetime from an API UTC time string."""
    naive = dt.datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%SZ')
    return naive.replace(tzinfo=dt.timezone.utc)

def parse_data(json_data):
    """Return list of CalendarEvents from the JSON data."""
    events = []
    if not json_data:
        return []
    for item in json_data['items']:
        n = item['summary']
        s = gtimepdt(item['start']['dateTime'])
        e = gtimepdt(item['end']['dateTime'])
        new_event = CalendarEvent(n, s, e)
        events.append(new_event)
    return events

def build_get(cal_id, key, end_min=None, start_max=None):
    """Return GET URL to receive the list of a calendar's events.
    
    Args:
        end_min (datetime): Optional, filter out events that end before this
        start_max (datetime): Optional, filter out events that start at or
            after this
    
    Returns:
        string: A URL of a GET for the calendar with the given query params
    """
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
    """Return a string of lines of status and name for events in the list."""
    lines = []
    for e in events:
        status = '{:\xa0>7}'.format(e.status(reference_time))
        lines.append('`|{:^9}|` **{}**'.format(status, e.name))
    return '\n'.join(lines)

