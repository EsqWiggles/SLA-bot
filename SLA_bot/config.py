import configparser
import datetime as dt

import pytz

default_config = configparser.ConfigParser(allow_no_value = True)
user_config = configparser.ConfigParser(allow_no_value = True)
user_config_path = 'Path not set'

bare_config = """[General]
bot_token = paste Discord bot token here
google_api_key = paste Google api key here

[Channels]"""

def channels():
    return [x[0] for x in user_config.items('Channels')]

def get(section, option):
    default = default_config.get(section, option)
    return user_config.get(section, option, fallback = default)

def getbool(section, option):
    opt = get(section, option)
    val = opt.lower()
    if val == 'true':
        return True
    if val == 'false':
        return False
    raise ValueError("Could not convert {} to bool".format(opt))
  
def getfloat(section, option):
    return float(get(section, option))
  
def getint(section, option):
    return int(get(section, option))
    
def gettdelta(section, option):
    return dt.timedelta(seconds = getint(section, option))
    
def gettimezone(section, option):
    return pytz.timezone(get(section, option))
    
def load_configs(default, user):
    default_config.read(default)
    user_config.read(user)
    global user_config_path
    user_config_path = user
    
def new_config(path):
    with open(path, 'w') as file:
        file.write(bare_config)

def reload():
    user_config.read(user_config_path)
    
def remove_option(section, option):
    return user_config.remove_option(section, option)
    
def save():
    with open(user_config_path, 'w') as configfile:
        user_config.write(configfile)
    
def section(name):
    if user_config.has_section(name):
        return user_config[name]
    return default_config[name]
    
def set(section, option, value):
    if not user_config.has_section(section):
        user_config.add_section(section)
    user_config.set(section, option, value)
