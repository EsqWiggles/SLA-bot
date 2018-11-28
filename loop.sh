#!/bin/bash
#screen -d -m this

while true; do
   python3.5 SLA-bot/sla_bot.py
   read -t 10 -p $'Retrying... press ENTER within 10 seconds to stop.\n'
   if [ $? == 0 ]; then
      break
   fi
done
