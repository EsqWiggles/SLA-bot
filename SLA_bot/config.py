import configparser
import collections
import datetime as dt
import os

import pytz

from SLA_bot.chanconfig import ChanConfig

class Config:

    #bytes to read at a time from http content
    chunk_size = 1024

    cal_url = 'http://www.google.com/calendar/ical/pso2emgquest%40gmail.com/public/basic.ics'

    #set full path from main file
    cal_path = os.path.join('usr', 'tmp', 'eq_schedule.ics')
    chan_path = os.path.join('usr', 'channels.ini')
    
    _user_cf = configparser.ConfigParser(allow_no_value = True)
    _chan_config = ChanConfig()
    
    custom_tz = collections.OrderedDict()
    alias={}
    
    _included_configs = []

    def parse_values(cf):
        Config.token = cf.get('Bot', 'token')
        Config.cmd_prefix = cf.get('Bot', 'cmd_prefix')
        Config.tz = pytz.timezone(cf.get('Bot', 'default_timezone'))
        Config.max_line = cf.getint('Bot', 'max_line')
        Config.chan_path = cf.get( 'Bot', 'chan_path', 
                                  fallback = Config.chan_path  )
        Config.enable_alert =  cf.getboolean('Bot', 'enable_alert')
        a_before = cf.getint('Bot', 'alert_before')
        Config.alert_before = dt.timedelta(minutes = a_before)
        r_before = cf.getint('Bot', 'resend_before')
        Config.resend_before = dt.timedelta(minutes = r_before)
        
        linked_configs = cf.get('Bot', 'include', fallback='').split(',')
        for path in linked_configs:
            if path:
                Config._included_configs.append(path)
        cf.set('Bot', 'include', '')
                                  
        Config.wkstart_weekday = cf.getint('EQ_Schedule', 'maint_weekday')
        Config.wkstart_time = cf.get('EQ_Schedule', 'maint_time')
        Config.cal_path = cf.get( 'EQ_Schedule', 'file_path', 
                                  fallback = Config.cal_path  )
        l_time = cf.getint('EQ_Schedule', 'linked_time')
        Config.linked_time = dt.timedelta(minutes=l_time)
        Config.refresh_time = cf.getint('EQ_Schedule', 'refresh_time')
        Config.find_default = cf.getint('EQ_Schedule', 'find_default')
        
        Config.custom_tz.update(cf.items('Timezones'))

        aliases = cf.items('Alias')
        for a in aliases:
            Config.alias[ a[0] ] = a[1].split(',,')
            
        Config._chan_config.read(Config.chan_path)
        Config.channels = Config._chan_config.parse()
        
    def load_config(file_paths):
        for file in file_paths:
            Config._user_cf.read(file)
        
        Config.parse_values(Config._user_cf)
        linked_configs = Config._included_configs
        Config._included_configs = []
        if len(linked_configs) > 0:
            Config.load_config(linked_configs)

    def dump_config(path):
        with open(path, "w") as config_file:
            Config._user_cf.write(config_file)
            
    def set_chan(id, filters):
        Config._chan_config.read(Config.chan_path)
        Config._chan_config.set(id, filters)
        Config._chan_config.write(Config.chan_path)
        Config.channels = Config._chan_config.parse()
        
    def delete_chans(ids):
        Config._chan_config.read(Config.chan_path)
        for i in ids:
            Config._chan_config.delete(i)
        Config._chan_config.write(Config.chan_path)
        Config.channels = Config._chan_config.parse()

