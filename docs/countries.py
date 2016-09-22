import pytz

for country_code, zones in sorted(pytz.country_timezones.items()):
    if len(zones) > 1:
        print('{:=^32}'.format(pytz.country_names[country_code]))
    for area in zones:
        print('{} = {}'.format(country_code.lower(), area))
    if len(zones) > 1:
        print('{:=^32}'.format('Pick one above'))
        
