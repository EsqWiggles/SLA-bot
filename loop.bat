@echo off
rem edit python_call and bot_path as needed
set python_call=python
set bot_path=sla_bot.py

for /l %%x in (1, 0, 2) do (
    echo ================ Restarting ================
    %python_call% %bot_path%
    timeout /t 20
)