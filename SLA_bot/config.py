"""Basic interface for interacting with config files.

Generally behaves like using configparser.py except it will try to read from the
user config first and reads from the default config as a fallback. Setting
values and saving them to file is only supported for the user config so the
default config is treated as if it is read-only.
"""

import configparser
import datetime as dt

import pytz

default_config = configparser.ConfigParser(allow_no_value = True)
default_config_path = ''
user_config = configparser.ConfigParser(allow_no_value = True)
user_config_path = ''

bare_config = """[General]
bot_token = paste Discord bot token here
google_api_key = paste Google api key here

[Channels]"""

def channels():
    """Return a list of channel IDs as strings from user config."""
    if 'Channels' not in user_config:
        return []
    return [x[0] for x in user_config.items('Channels')]

def get(section, option):
    """Return the option value in section from user or default config."""
    default = default_config.get(section, option)
    return user_config.get(section, option, fallback = default)

def getbool(section, option):
    """Return option value in section as a boolean."""
    opt = get(section, option)
    val = opt.lower()
    if val == 'true':
        return True
    if val == 'false':
        return False
    raise ValueError("Could not convert {} to bool".format(opt))
  
def getfloat(section, option):
    """Return option value in section as a float."""
    return float(get(section, option))
  
def getint(section, option):
    """Return option value in section as an int."""
    return int(get(section, option))
    
def gettdelta(section, option):
    """Return option value in section as a timedelta."""
    return dt.timedelta(seconds = getint(section, option))
    
def gettimezone(section, option):
    """Return option value in section as a pytz time zone."""
    return pytz.timezone(get(section, option))
    
def load_configs(default, user):
    """Read the given config file paths into their respective config object."""
    default_config.read(default)
    user_config.read(user)
    global default_config_path
    global user_config_path
    default_config_path = default
    user_config_path = user
    
def new_config(path):
    """Write a minimal user config at the file path."""
    with open(path, 'w') as file:
        file.write(bare_config)

def reload():
    """Re-read the user and default config."""
    default_config.read(default_config_path)
    user_config.read(user_config_path)
    
def remove_option(section, option):
    """Remove the option in section from the user config."""
    return user_config.remove_option(section, option)
    
def save():
    """Write the current user config object's values into the file."""
    with open(user_config_path, 'w') as configfile:
        user_config.write(configfile)
    
def section(name):
    """Return the section (ordered dictionary) from user or default config."""
    if user_config.has_section(name):
        return user_config[name]
    return default_config[name]
    
def set(section, option, value):
    """Set the option value into the section of the user config object."""
    if not user_config.has_section(section):
        user_config.add_section(section)
    user_config.set(section, option, value)
