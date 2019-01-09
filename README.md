## Description

Discord bot that gathers external information about PSO2, including emergency
quest schedules and RSS links.

## Installation

### Python
Python 3.5 or later is required, along with 3 additional packages:
```
python -m pip install -U discord.py
python -m pip install -U pytz
python -m pip install -U aiohttp
```
If your system has multiple python version make sure to call the right python version.

### Discord
1. Sign up for a [Discord](https://discordapp.com/) account
2. Navigate to the [developer portal](https://discordapp.com/developers/applications/)
3. Click "Create an application"
4. Optionally give it a name and picture
5. Keep this page open for later config instructions

### Google
1. Sign up for a Google account
2. Open the [Google APIs](https://console.developers.google.com/cloud-resource-manager) page
3. Create a project
4. Enable APIs and Services
5. Search for and enable **Google Calendar** and **URL shortner**
6. Go to the credentials page and keep it open for later config instructions

### This Bot
1. Get this project using git or download its zip from GitHub and extract it
2. Navigate to the project folder and run the bot `python sla_boy.py`
3. Go to the Discord page from earlier, copy the **CLIENT SECRET**, and paste into config.ini after
   `bot_token = `
4. Go to the Google page from earlier, copy the **API key**, and paste into config.ini after
   `google_api_key = `
5. The bot should run now `python sla_boy.py`
6. Go back to the Discord page from earlier, click the OAuth2 tab and select:
    * **bot** in Scope
    * **Send Messages** in Permissions
    * **Read Message History** in Permissions
7. Copy the generated link and give it to server admins who want to invite the bot
8. Have the admin create a channel for the bot and type `;toggle` in it

## Usage

### Operating the bot
Run `python sla_boy.py` or use the loop scripts `loop.bat` for windows or `./loop.sh` on linux. The
default config contains examples of changeable parameters in the bot and restart the bot after
editing it. 

### Commands
Summary of availiable commands for users. For more detailed information and examples, use `help`.
* `help (command)`: Receive a help message about the bot or detailed information about the command
* `find (text)`: List the next few events with names partially matching the text
* `next`: Show the next event
* `toggle`: Enable/Disable the bot's automatic message (requires **Manage Channels** permission)


## License

This project is licensed under the [MIT License](LICENSE).
