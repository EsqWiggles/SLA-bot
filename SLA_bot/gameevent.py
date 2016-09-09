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


class MultiShipEvent(GameEvent):
    def __init__(self, name, ships, start, end = None):
        super().__init__(name, start, end)
        self.ships = ships
        self.unscheduled = False
        for event in self.ships[1:]:
            if event:
                self.unscheduled = True

    def multi_dur(self, targets, tz):
        if self.unscheduled == False:
            return self.ships[0]
        
        ship_events = []
        for index in targets:
            line = '`ship {:02d}: `{}'.format(index, self.ships[index])
            ship_events.append(line)
        if len(ship_events) < 1:
            return ''
        
        header = self.duration(tz)
        body = '\n'.join(ship_events)
        return '{}\n{}'.format(header, body)

    def __repr__(self):
        return 'MultiShipEvent({}, {}, {}, {})'.format(self.name, self.ships,
                                                       self.start, self.end)