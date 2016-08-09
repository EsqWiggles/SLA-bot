import configparser
import os

class Config:

    #bytes to read at a time from http content
    chunk_size = 1024

    config_path = os.path.abspath(os.path.join(__file__, '../../config.ini'))

    cal_url = 'http://www.google.com/calendar/ical/pso2emgquest%40gmail.com/public/basic.ics'

    cal_path = os.path.abspath(os.path.join(__file__, '../../usr/calendar/eq_schedule.ics'))

    _user_cf = configparser.ConfigParser(allow_no_value = True)

    def make_default(cf):
        cf.add_section('Bot')
        cf.set('Bot', 'token', 'paste_bot_token_here')
        cf.set('Bot', 'default_timezone', 'Asia/Tokyo')
        cf.add_section('EQ_Schedule')
        cf.set('EQ_Schedule', 'maint_weekday', '3')
        cf.set('EQ_Schedule', 'maint_time', '02:00:00')
        cf.set('EQ_Schedule', 'file_path', Config.cal_path)
        cf.add_section('Timezones')
        for value in Config._default_custom_tz:
            if type(value) is tuple:
                cf.set('Timezones', value[0], value[1])
            else:
                cf.set('Timezones', value)

    def parse_values(cf):
        Config.token = cf.get('Bot', 'token')
        Config.tz = cf.get('Bot', 'default_timezone')
        Config.wkstart_weekday = cf.getint('EQ_Schedule', 'maint_weekday')
        Config.wkstart_time = cf.get('EQ_Schedule', 'maint_time')
        Config.cal_path = cf.get('EQ_Schedule', 'file_path')
        Config.custom_tz = dict(cf.items('Timezones'))
        
    def load_config():
        Config.make_default(Config._user_cf)
        Config._user_cf.read(Config.config_path)
        Config.parse_values(Config._user_cf)

    _default_custom_tz =[
        ('ar', 'America/Argentina/Buenos_Aires'),
        ('au', 'Australia/Sydney'),
        ('br', 'America/Sao_Paulo'),
        ('ca', 'America/Toronto'),
        ('cd', 'Africa/Kinshasa'),
        ('cl', 'America/Santiago'),
        ('cn', 'Asia/Shanghai'),
        ('de', 'Europe/Berlin'),
        ('ec', 'America/Guayaquil'),
        ('es', 'Europe/Madrid'),
        ('fm', 'Pacific/Pohnpei'),
        ('gl', 'America/Godthab'),
        ('id', 'Asia/Kolkata'),
        ('ki', 'Pacific/Tarawa'),
        ('kz', 'Asia/Almaty'),
        ('mh', 'Pacific/Majuro'),
        ('mn', 'Asia/Ulaanbaatar'),
        ('my', 'Asia/Kuala_Lumpur'),
        ('mx', 'America/Mexico_City'),
        ('nz', 'Pacific/Auckland'),
        ('pf', 'Pacific/Tahiti'),
        ('pg', 'Pacific/Port_Moresby'),
        ('ps', 'Asia/Gaza'),
        ('pt', 'Europe/Lisbon'),
        ('ru', 'Europe/Moscow'),
        ('ua', 'Europe/Kiev'),
        ('um', 'Pacific/Johnston'),
        ('us', 'America/New_York'),
        ('uz', 'Asia/Tashkent')
    ]

if __name__=='__main__':
    default_cf = os.path.abspath(os.path.join(__file__, '../default_config.ini'))
    Config.make_default(Config._user_cf)
    with open(default_cf, "w") as config_file:
        Config._user_cf.write(config_file)

