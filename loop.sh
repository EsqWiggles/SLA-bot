#!/bin/bash
#screen -d -m this
#edit python_call and bot_path as needed
python_call=python3
bot_path=sla_bot.py

while true; do
   $python_call $bot_path
   read -t 20 -p $'Retrying... press ENTER within 20 seconds to stop.\n'
   if [ $? == 0 ]; then
      break
   fi
done
