# The Best discord bot for the Best server in existence
## Implementation
This bot is implemented using the [`interactions.py`](https://interactions-py.github.io/interactions.py/) library and uses async/await operations

## Development
### Creating your own bot instance for testing
I highly recommend creating your own instance of a bot on your own server for development and testing purposes. You can do so at [`Discord Development Portal`](https://discord.com/developers/applications)
### Required permissions for the bot
In the `App->Settings->Bot` section, save the token that will be required for the `.env` file and tick all `Privileged Gateway Intents` checkboxes (PRESENCE INTENT, SERVER MEMBERS INTENT, MESSAGE CONTENT INTENT)
### Inviting the bot to a server
In the `App-Settings-OAuth2->URL Generator` section, tick all these checkboxes:
- in `SCOPES`
    - bot
    - applications.commands
- in `BOT PERMISSIONS`
    - Manage Roles
    - Read Messages/View Channels
    - Send Messages

Copy the generated URL below, paste it into a new browser window and follow the instructions. If there are any complications with the bot on your server, it's most likely that there is a mistake in these checkboxes, you will have to experiment with them and repeat the bot inviting process. Similarly, if there would be any new required permissions (or the ones I forgot to mention), please add them into this README
### Setting up local development environment
Install all the requirements using `pip install -r requirements.txt`. You will also need a `.env` file, feel free to use this template:
```python
TOKEN=          # token from the Application on Discord Development Portal
NERD_USER=      # arbitrary field holding an user id, as of now, it has no use in the code, but must be set to 0
BAN_ROLE=       # role_id that is given to the user getting banned
NORMAL_ROLE=    # role_id that all verified users have
HLASKA_ROLE=    # role_id for role that enables #hlasouanie channel for users
VAZENIE_ROOM=   # channel_id of the channel designated for banned users
BOT_ROOM=       # channel_id of the channel designated for bot messages
```
These are all the necessary fields required so far, feel free to add more
### Launching the bot
Navigate into the root folder and run the `bot.py` file with your preferred python3 interpreter

## Contributing to this repository
As mentioned previously, if you were to change the `.env` file or to add new permissions, please add those changes into this README. Any new planned features are in the `todo.md` file
### Changelog
Any new changes that would alter the behavior or add new features and bugfixes should be mentioned in this file. Please respect the structure and follow it. Internal implementation changes such as refactoring or restructuring should not be mentioned in the changelog. To mention yourself in the changelog, your ID will be required, you can add it as a new field in the `.env` file, the example to do so is in the `bot.py:whats_new()` function