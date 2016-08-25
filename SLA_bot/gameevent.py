class GameEvent:
    def __init__(self, name, start, end = None):
        self.name = name
        self.start = start
        self.end = end
        
    @classmethod
    def from_ical(cls, component):
        n = component.get('summary')
        s = component.get('dtstart').dt
        e = getattr(component.get('dtend'), 'dt', None)
        return cls(n, s, e)
    
    def duration(self, tz):
        s = self.start.astimezone(tz)
        s_dt = s.strftime('%b %d, %H:%M')
        tz_str= s.strftime('%Z')
        try:
            e_time  = self.end.astimezone(tz).strftime('%H:%M')
        except AttributeError:
            return '**{}** @ {} {}'.format(self.name, s_dt, tz_str)
        return '**{}** @ {} - {} {}'.format(self.name, s_dt, e_time, tz_str)
    
    def __repr__(self):
        return 'GameEvent({}, {}, {})'.format(self.name, self.start, self.end)

