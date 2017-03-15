import configparser
import datetime as dt

import pytz

_config_parser = configparser.ConfigParser(allow_no_value = True)
_user_conf = configparser.ConfigParser(allow_no_value = True)
user_config_path = 'Path not set'

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
        ids = cf.items('Channels')
        cls.id_chan = {}
        for i in ids:
            cls.id_chan[i] = ''

    @classmethod
    def load_channels(cls, bot):
        for i in cls.id_chan:
            cls.id_chan[i] = bot.get_channel(i)

    @classmethod        
    def add(cls, channel_obj):
        reload()
        try:
            _user_conf.add_section(cls.section)
        except configparser.DuplicateSectionError:
            pass
        _config_parser.set(cls.section, channel_obj.id, '')
        _user_conf.set(cls.section, channel_obj.id, '')
        cls.id_chan[channel_obj.id] = channel_obj
        save()

    @classmethod    
    def remove(cls, id):
        reload()
        _config_parser.remove_option(cls.section, id)
        _user_conf.remove_option(cls.section, id)
        del cls.id_chan[id]
        save()

def parse_config():
    for component in (general, clock, pso2cal, pso2feed, channels):
        component.parse(_config_parser)

def load_configs(default, user = None):
    _config_parser.read(default)
    if user:
        _config_parser.read(user)
        _user_conf.read(user)
        global user_config_path
        user_config_path = user
 
    
    parse_config()

def reload():
    _config_parser.read(user_config_path)
    _user_conf.read(user_config_path)
    parse_config()

def save():
    with open(user_config_path, 'w') as configfile:
        _user_conf.write(configfile)