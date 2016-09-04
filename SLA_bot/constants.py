BOT_HELP = '''A bot for displaying Phantasy Star Online 2 events.

This bot is currently at a very basic level.
There are still some usability issues like choosing time zones.
Announcements for scheduled and unscheduled events are planned.'''

FUTURE_HELP = '''Find future scheduled events by name.
Future takes in two options, "search" and "timezone" in this order.

    search: a partial name of the event, example: apocalypse
        (defaults to displaying the next several events)

    timezone: (defaults to the bot's chosen time zone)
        CC - two letter country code, example: jp (Japan)
        +## - UTC offset example: +9 (Japan),  -8 (North America PST)

        For people who live in countries with multiple time zones, your
        country code will pick a single time zone (typically the capital).
        Please find your UTC/GMT offset and use that instead. The offset
        for your time zone also changes during daylight saving time. For
        example: PST -8, PDT -7.'''

LAST_HELP = '''Find the last scheduled event by name.
Last takes in two options, "search" and "timezone" in this order.

    search: a partial name of the event, example: apocalypse
        (defaults to displaying any event)

    timezone: (defaults to the bot's chosen time zone)
        CC - two letter country code, example: jp (Japan)
        +## - UTC offset example: +9 (Japan),  -8 (North America PST)

        For people who live in countries with multiple time zones, your
        country code will pick a single time zone (typically the capital).
        Please find your UTC/GMT offset and use that instead. The offset
        for your time zone also changes during daylight saving time. For
        example: PST -8, PDT -7.'''

NEXT_HELP = '''Find the next scheduled event by name.
Next takes in two options, "search" and "timezone" in this order.

    search: a partial name of the event, example: apocalypse
        (defaults to displaying any event)

    timezone: (defaults to the bot's chosen time zone)
        CC - two letter country code, example: jp (Japan)
        +## - UTC offset example: +9 (Japan),  -8 (North America PST)

        For people who live in countries with multiple time zones, your
        country code will pick a single time zone (typically the capital).
        Please find your UTC/GMT offset and use that instead. The offset
        for your time zone also changes during daylight saving time. For
        example: PST -8, PDT -7.'''

PRINT_HELP = '''Print the scheduled events on the date based on the time zone.
Print takes in two options, "date" and "timezone" in this order.

    date: the following keywords or a date YYYY/MM/DD, example: 2014/12/30
        today - today's events
        tomorrow - tomorrow's events 
        yesterday - yesterday's events
        week - all events from last maintenance to next maintenance
        future - all future events (usually to next maintenance)
        (defaults to "today")

        *Note: You can enter a partial MM/DD or DD date like 12/30 or 30,
        respectively, and it will try to guess the rest. If it does not
        pick the date you want, please use the precise YYYY/MM/DD format.

    timezone: (defaults to the bot's chosen time zone)
        CC - two letter country code, example: jp (Japan)
        +## - UTC offset example: +9 (Japan),  -8 (North America PST)
        
        For people who live in countries with multiple time zones, your
        country code will pick a single time zone (typically the capital).
        Please find your UTC/GMT offset and use that instead. The offset
        for your time zone also changes during daylight saving time. For
        example: PST -8, PDT -7.'''
        




