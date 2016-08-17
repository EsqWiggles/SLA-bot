import configparser
import os

import pytz

class Config:

    #bytes to read at a time from http content
    chunk_size = 1024

    cal_url = 'http://www.google.com/calendar/ical/pso2emgquest%40gmail.com/public/basic.ics'

    cal_path = os.path.abspath(os.path.join(__file__, '../../usr/calendar/eq_schedule.ics'))

    _user_cf = configparser.ConfigParser(allow_no_value = True)
    
    custom_tz={}
    alias={}

    def parse_values(cf):
        Config.token = cf.get('Bot', 'token')
        Config.tz = pytz.timezone(cf.get('Bot', 'default_timezone'))
        Config.wkstart_weekday = cf.getint('EQ_Schedule', 'maint_weekday')
        Config.wkstart_time = cf.get('EQ_Schedule', 'maint_time')
        Config.cal_path = cf.get('EQ_Schedule', 'file_path')
        Config.custom_tz.update(cf.items('Timezones'))
        
        aliases = cf.items('Alias')
        for a in aliases:
            Config.alias[ a[0] ] = a[1].split(',,')

        
    def load_config(file_paths):
        for file in file_paths:
            Config._user_cf.read(file)
        Config.parse_values(Config._user_cf)

    def dump_config(path):
        with open(path, "w") as config_file:
            Config._user_cf.write(config_file)

    

