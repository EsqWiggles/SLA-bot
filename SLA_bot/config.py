import configparser
import datetime as dt

import pytz

_config_parser = configparser.ConfigParser(allow_no_value = True)

def getsec(parser, section, option):
    return dt.timedelta(seconds = parser.getint(section, option))

class general:
    section = 'General'
    @classmethod
    def parse(cls, cf):
        cls.cmd_prefix = cf.get(cls.section, 'command_prefix')
        cls.google_key = cf.get(cls.section, 'google_api_key')
        cls.timezone = pytz.timezone( cf.get(cls.section, 'timezone') )
        cls.token = cf.get(cls.section, 'bot_token')

class clock:
    section = 'Clock'
    @classmethod
    def parse(cls, cf):
        cls.header = cf.get(cls.section, 'header')
        cls.interval = getsec(cf, cls.section, 'update_interval')

class pso2cal:
    section = 'PSO2 Calendar'
    @classmethod
    def parse(cls, cf):
        cls.header = cf.get(cls.section, 'header')
        cls.interval = getsec(cf, cls.section, 'update_interval')
        cls.range = getsec(cf, cls.section, 'time_range')
        
class pso2feed:
    section = 'PSO2 Feed'
    @classmethod
    def parse(cls, cf):
        cls.header = cf.get(cls.section, 'header')
        cls.interval = getsec(cf, cls.section, 'update_interval')

class channels:
    section = 'Channels'
    @classmethod
    def parse(cls, cf):
        cls.ids = cf.items('Channels')
        cls.objs = {}

    @classmethod
    def load_channels(cls, bot):
        for i in cls.ids:
            cls.objs[i] = bot.get_channel(i)

    @classmethod        
    def add(cls, channel_obj):
        cls.ids[channel_obj.id] = ''
        cls.objs[channel_obj.id] = channel_obj

    @classmethod    
    def remove(cls, id):
        del cls.ids[id]
        del cls.objs[id]


def load_configs(file_paths):
    for file in file_paths:
        _config_parser.read(file)
    
    for component in (general, clock, pso2cal, pso2feed, channels):
        component.parse(_config_parser)

