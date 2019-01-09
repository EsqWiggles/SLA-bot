BOT_HELP = ('Pulls together various Phantasy Star Online 2 information.\n'
'\n'
'Provides a clock, information from Emergency Quest calendars, and unscheduled'
' events.')

FIND_HELP = ('Find upcoming events by name.\n'
'search (optional): a partial name of the event\n'
'    Find events with the text given, ignoring case.\n'
'    Leave blank to find any event.\n'
'\n'
'mode (optional): all\n'
'    Output all of the events and whisper if too long.\n'
'    Leave blank to shorten it and reply in the channel.\n'
'\n'
'This command will count the number of events with names matching the search.'
' To prevent long messages, this command does not show every event that'
' matches unless the mode option was set to "all".\n'
'\n'
'Examples:\n'
'    find              (shows the next few events)\n'
'    find minING       (ignores weird capital)\n'
'    find "mining base"(need quotes for two words)\n'
'    find "" all       (need quotes for blank search)')

NEXT_HELP = ('Find the next scheduled event.\n'
'Shows the current event if it has not ended and the next event.'
' May show another event if its start time is close together.')

TOGGLE_HELP = ('Enable or disable the bot data on a channel.\n'
"Enables the automatic bot's messages in the channel.This should be used on a"
' dedicated channel or on one that receives few messages. If the bot messages'
' gets pushed too far into chat history, it will send new messages when it'
' crashes or restarts.\n'
'\n'
'To disable on a channel, use this command on the channel again.\n'
'\n'
'This command requires the user to have "Manage Channels" permission.')

