import configparser
import os

#bytes to read at a time from http content
chunk_size = 1024

config_path = os.path.abspath(os.path.join(__file__, '../../config.ini'))

cal_url = 'http://www.google.com/calendar/ical/pso2emgquest%40gmail.com/public/basic.ics'

cal_path = os.path.abspath(os.path.join(__file__, '../../usr/calendar/eq_schedule.ics'))


config = configparser.ConfigParser(allow_no_value = True)

def make_default():
    config.add_section('Bot')
    config.set('Bot', 'token', 'paste_bot_token_here')
    config.set('Bot', 'default_timezone', 'Asia/Tokyo')
    config.add_section('EQ_Schedule')
    config.set('EQ_Schedule', 'maint_weekday', '3')
    config.set('EQ_Schedule', 'maint_time', '02:00:00')
    config.set('EQ_Schedule', 'file_path', cal_path)
    
def load_config():
    make_default()
    config.read(config_path)

if __name__=='__main__':
    make_default()
    with open(config_path, "w") as config_file:
        config.write(config_file)

    