class GameEvent:
    def __init__(self, name, start, end = None):
        self.name = name
        self.start = start
        self.end = end
        
    def __eq__(self, other):
        return (self.name == other.name and self.start == other.start and
               self.end == other.end)
        
    def __hash__(self):
        return hash((self.name, self.start, self.end))
        
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
        self.ships = tuple(ships)
        self.unscheduled = False
        
        for event in self.ships[1:]:
            if event:
                self.unscheduled = True

    def __eq__(self, other):
        return super.__eq__(self, other) and self.ships == other.ships
        
    def __hash__(self):
        return hash((self.name, self.start, self.end, self.ships))

    def ship_prefix(num):
        return '`ship {:02d}:`'.format(num)
        
    def filter_ships(text, ships):
        lines = text.splitlines(keepends=True)
        for num in ships:
            prefix = MultiShipEvent.ship_prefix(num)
            lines = [x for x in lines if not x.startswith(prefix)]
        
        if len(lines) > 1:
            return ''.join(lines)
            
        #Only has header, better to display nothing
        return ''
                
    def duration(self, tz):
        if self.unscheduled == False:
            return self.ships[0]
        
        ship_events = []
        for index in range(1, len(self.ships)):
            line = MultiShipEvent.ship_prefix(index) + self.ships[index]
            ship_events.append(line)
            
        header = super().duration(tz)
        body = '\n'.join(ship_events)
        return '{}\n{}'.format(header, body)

    def __repr__(self):
        return 'MultiShipEvent({}, {}, {}, {})'.format(self.name, self.ships,
                                                       self.start, self.end)