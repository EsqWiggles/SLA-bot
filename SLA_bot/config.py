import os

#bytes to read at a time from http content
chunk_size = 1024

cal_path = os.path.abspath(os.path.join(__file__, '../../usr/calendar/eq_schedule.ics'))
cal_url = 'http://www.google.com/calendar/ical/pso2emgquest%40gmail.com/public/basic.ics'

#utc
maint_weekday = 3
maint_time='08:00:00'