import datetime as dt

class EventDir:
    def __init__(self, events):
        self.events = events
        self.bydate = {}
        self.byname = {}
        
        last = -1
        now = dt.datetime.now(dt.timezone.utc)
        for i, e in enumerate(self.events):
            try:
                self.bydate[e.start.date()].append(i)
            except KeyError:
                self.bydate[e.start.date()] = [i]
                
            try:
                self.byname[e.name.lower()].append(i)
            except KeyError:
                self.byname[e.name.lower()] = [i]
            
            if e.start <= now:
                last = i
        self.__next = last + 1
        
        self.dates = list(self.bydate)
        self.dates.sort()
        self.names = list(self.byname)
    
    @property
    def beg(self):
        return 0

    @property
    def end(self):
        return len(self.events)
    
    @property
    def next(self):
        now = dt.datetime.now(dt.timezone.utc)        
        while self.__next < self.end and now >= self.events[self.__next].start:
            self.__next += 1
        return self.__next
        
    @property
    def last(self):
        return self.next - 1

    def indexfdt(self, some_dt):
        try:
            day = self.bydate[some_dt.date()]
            for i in day:
                if self.events[i].start >= some_dt:
                    return i
            return i + 1
        except KeyError:
            for date in self.dates:
                if date > some_dt.date():
                    return self.bydate[date][0]
        return self.end
        
    def rangefdt(self, start=None, end=None):
        lower_bound = self.beg if start == None else self.indexfdt(start)
        upper_bound = self.end if   end == None else self.indexfdt(end)
        return (lower_bound, upper_bound)
        
    def find(self, search):
        matched = [x for x in self.names if search.lower() in x]
        found = []
        for m in matched:
            found.extend(self.byname[m])
        found.sort()
        return found


