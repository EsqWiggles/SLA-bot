@echo off
for /l %%x in (1, 0, 2) do (
    echo ================ Restarting ================
    python sla_bot.py
    timeout /t 20
)