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
        ';Example of custom keywords',
        (';aedt', 'Australia/Sydney'),
        (';aest', 'Australia/Brisbane'),
        (';acdt', 'Australia/Adelaide'),
        (';acst', 'Australia/Darwin'),
        (';awst', 'Australia/Perth'),
        (';akst', 'America/Anchorage'),
        (';cst', 'America/Chicago'),
        (';est', 'America/New_York'),
        (';mst', 'America/Denver'),
        (';pst', 'America/Los_Angeles'),
        (';hst', 'Pacific/Honolulu'),
        (';nst', 'America/St_Johns'),
        (';ast', 'America/Halifax'),
        ';List of countries with multiple timezones.',
        ';Use this as a reference to make custom keywords.',
        ';If the timezone has a different area between its',
        ';daylight saving and standard time, it means there is',
        ';an area that does not observe daylight savings time.',
        ';A full list of areas and cities can be found at:,',
        ';https://en.wikipedia.org/wiki/List_of_tz_database_time_zones',
        ';;',
        ';Australia',
        ('au', 'Australia/Sydney'),
        (';au-aedt', 'Australia/Sydney'),
        (';au-aest', 'Australia/Brisbane'),
        (';au-acdt', 'Australia/Adelaide'),
        (';au-acst', 'Australia/Darwin'),
        (';au-acwst', 'Australia/Eucla'),
        (';au-awst', 'Australia/Perth'),
        (';au-lhst', 'Australia/Lord_Howe'),
        (';au-mist', 'Antarctica/Macquarie'),
        ';Brazil',
        ('br', 'America/Sao_Paulo'),
        (';br-act', 'America/Rio_Branco'),
        (';br-amst', 'America/Campo_Grande'),
        (';br-amt', 'America/Manaus'),
        (';br-fnt', 'America/Noronha'),
        (';br-brst', 'America/Sao_Paulo'),
        (';br-brt', 'America/Fortaleza'),
        (';br-brt-2', 'America/Rio_Branco'),
        (';br-brt-1', 'America/Manaus'),
        (';br-brt+1', 'America/Noronha'),
        ';Canada',
        ('ca', 'America/Toronto'),
        (';ca-adt', 'America/Halifax'),
        (';ca-ast', 'America/Blanc-Sablon '),
        (';ca-cdt', 'America/Winnipeg'),
        (';ca-cst', 'America/Regina'),
        (';ca-edt', 'America/Toronto'),
        (';ca-est', 'America/Atikokan'),
        (';ca-mdt', 'America/Edmonton'),
        (';ca-mst', 'America/Dawson_Creek'),
        (';ca-ndt', 'America/St_Johns'),
        (';ca-nst', 'America/St_Johns'),
        (';ca-pdt', 'America/Vancouver'),
        (';ca-pst', 'America/Vancouver'),
        ';Democratic Republic of Congo',
        ('cd', 'Africa/Kinshasa'),
        (';cd-cat', 'Africa/Lubumbashi'),
        (';cd-wat', 'Africa/Kinshasa'),
        ';Chile',
        ('cl', 'America/Santiago'),
        (';cl-clst', 'America/Santiago'),
        (';cl-clt', 'America/Santiago'),
        (';cl-east', 'Pacific/Easter'),
        ';Spain',
        ('es', 'Europe/Madrid'),
        (';es-cest', 'Europe/Madrid'),
        (';es-cet', 'Europe/Madrid'),
        (';es-west', 'Atlantic/Canary'),
        (';es-wet', 'Atlantic/Canary'),
        ';Ecuador',
        ('ec', 'America/Guayaquil'),
        (';ec-ect= America/Guayaquil'),
        (';ec-galt', 'Pacific/Galapagos'),
        ';Federated States of Micronesia',
        ('fm', 'Pacific/Pohnpei'),
        (';fm-chut', 'Pacific/Chuuk'),
        (';fm-kost', 'Pacific/Kosrae'),
        (';fm-pont', 'Pacific/Pohnpei'),
        ';Greenland',
        ('gl', 'America/Godthab'),
        (';gl-adt', 'America/Thule'),
        (';gl-ast', 'America/Thule'),
        (';gl-egst', 'Scoresbysund'),
        (';gl-egt', 'Scoresbysund'),
        (';gl-gmt', 'America/Danmarkshavn'),
        (';gl-wgst', 'America/Godthab'),
        (';gl-wgt', 'America/Godthab'),
        ';Kiribati',
        ('ki', 'Pacific/Tarawa'),
        (';ki-gilt', 'Pacific/Tarawa'),
        (';ki-lint', 'Pacific/Kiritimati'),
        (';ki-phot', 'Pacific/Enderbury'),
        ';Kazakhstan',
        ('kz', 'Asia/Almaty'),
        (';kz-east', 'Asia/Almaty'),
        (';kz-west', 'Asia/Aqtobe'),
        ';Myanmar',
        ('mn', 'Asia/Ulaanbaatar'),
        (';mn-hovst', 'Asia/Hovd'),
        (';mn-hovt', 'Asia/Hovd'),
        (';mn-ulast', 'Asia/Ulaanbaatar'),
        (';mn-ulat', 'Asia/Ulaanbaatar'),
        ';Mexico',
        ('mx', ' America/Mexico_City'),
        (';mx-cdt', 'America/Mexico_City'),
        (';mx-cst', 'America/Mexico_City'),
        (';mx-est', 'America/Cancun'),
        (';mx-mdt', 'America/Chihuahua'),
        (';mx-mst', 'America/Hermosillo'),
        (';mx-pdt', 'America/Tijuana'),
        (';mx-pst', 'America/Tijuana'),
        ';New Zealand',
        ('nz', 'Pacific/Auckland'),
        (';nz-nzst', 'Pacific/Auckland'),
        (';nz-ndst', 'Pacific/Auckland'),
        (';nz-chast', 'Pacific/Chatham'),
        (';nz-chadt', 'Pacific/Chatham'),
        ';French Polynesia',
        ('pf', 'Pacific/Tahiti'),
        (';pf-gamt', 'Pacific/Gambier'),
        (';pf-mart', 'Pacific/Marquesas'),
        (';pf-taht', 'Pacific/Tahiti'),
        ';Papua New Guinea',
        ('pg', 'Pacific/Port_Moresby'),
        (';pg-bst', 'Pacific/Bougainville'),
        (';pg-pgt', 'Pacific/Port_Moresby'),
        ';Portugal',
        ('pt', 'Europe/Lisbon'),
        (';pt-west', 'Europe/Lisbon'),
        (';pt-wet', 'Europe/Lisbon'),
        (';pt-azost', 'Atlantic/Azores'),
        (';pt-azot', 'Atlantic/Azores'),
        ';Russian Federation',
        ('ru', 'Europe/Moscow'),
        (';ru-anat', 'Asia/Anadyr'),
        (';ru-msk', 'Europe/Moscow'),
        (';ru-eet', 'Europe/Kaliningrad'),
        (';ru-irkt', 'Asia/Irkutsk'),
        (';ru-krat', 'Asia/Krasnoyarsk'),
        (';ru-magt', 'Asia/Magadan'),
        (';ru-novt', 'Asia/Novosibirsk'),
        (';ru-omst', 'Asia/Omsk'),
        (';ru-pett', 'Asia/Kamchatka'),
        (';ru-sakt', 'Asia/Sakhalin'),
        (';ru-samt', 'Europe/Samara'),
        (';ru-sret', 'Asia/Srednekolymsk'),
        (';ru-vlat', 'Asia/Vladivostok'),
        (';ru-yakt', 'Asia/Yakutsk'),
        (';ru-yekt', 'Asia/Yekaterinburg'),
        ';United States Minor Outlying Islands',
        ('um', 'Pacific/Johnston'),
        (';um-hst', 'Pacific/Johnston'),
        (';um-sst', 'Pacific/Midway'),
        (';um-wakt', 'Pacific/Wake'),
        ';United States of America',
        ('us', 'America/New_York'),
        (';us-akdt', 'America/Anchorage'),
        (';us-akst', 'America/Anchorage'),
        (';us-cdt', 'America/Chicago'),
        (';us-cst', 'America/Chicago'),
        (';us-est', 'America/New_York'),
        (';us-edt', 'America/New_York'),
        (';us-mdt', 'America/Denver'),
        (';us-mst', 'America/Phoenix'),
        (';us-pdt', 'America/Los_Angeles'),
        (';us-pst', 'America/Los_Angeles'),
        (';us-hadt', 'America/Adak'),
        (';us-hst', 'Pacific/Honolulu'),
        ';;;',
        ';The following countries have multiple',
        ';areas listed but use only one timezone',
        ('ar', 'America/Argentina/Buenos_Aires'),
        ('cn', 'Asia/Shanghai'),
        ('de', 'Europe/Berlin'),
        ('id', 'Asia/Kolkata'),
        ('mh', 'Pacific/Majuro'),
        ('my', 'Asia/Kuala_Lumpur'),
        ('ps', 'Asia/Gaza'),
        ('ua', 'Europe/Kiev'),
        ('uz', 'Asia/Tashkent'),

    ]

if __name__=='__main__':
    default_cf = os.path.abspath(os.path.join(__file__, '../default_config.ini'))
    Config.make_default(Config._user_cf)
    with open(default_cf, "w") as config_file:
        Config._user_cf.write(config_file)

