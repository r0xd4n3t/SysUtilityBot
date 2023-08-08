<a id="top"></a>

#

<h1 align="center">
SysUtilityBot
</h1>

<p align="center"> 
  <kbd>
<img src="https://raw.githubusercontent.com/r0xd4n3t/SysUtilityBot/main/img/tbot.png"></img>
  </kbd>
</p>

<p align="center">
<img src="https://img.shields.io/github/last-commit/r0xd4n3t/SysUtilityBot?style=flat">
<img src="https://img.shields.io/github/stars/r0xd4n3t/SysUtilityBot?color=brightgreen">
<img src="https://img.shields.io/github/forks/r0xd4n3t/SysUtilityBot?color=brightgreen">
</p>

"A Python-based Telegram bot for real-time system monitoring &amp; remote commands. Manage users, monitor CPU, memory, disk, &amp; network. Execute commands remotely."

# 📜 Introduction
This repository contains a Telegram bot written in Python that provides various system-related information and allows remote execution of commands on the host system. The bot is designed to be run on a server or machine that you want to monitor remotely. It can be especially useful for system administrators or power users who need to keep an eye on their system's performance and perform administrative tasks remotely.

The bot comes with a set of commands to view system information, manage admin and user access, execute commands on the host system, and more. It also supports logging and can handle exceptions, ensuring a smooth user experience.

## 📝 Prerequisites
- Python 3.10 or higher
- python-telegram-bot library

Create a Telegram bot and get your bot token. Follow the official Telegram documentation to create a new bot and obtain the token.

### 🔄 Install
1. Clone the repository and navigate to the SysUtilityBot directory:
```
git clone https://github.com/r0xd4n3t/SysUtilityBot.git
cd SysUtilityBot
```
2. Install the required dependencies using `pip`:
```
pip3.10 install -r requirements.txt
```
3. Edit `config.json` file:
```
{
    "telegram_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "allowed_group": YOUR_ALLOWED_GROUP_ID,
    "admin_ids": [
        ADMIN1_ID,
        ADMIN2_ID
    ],
    "user_ids": [
        USER1,
        USER2
    ],
    "god_chat_id": YOUR_GOD_CHAT_ID
}
```
Replace YOUR_TELEGRAM_BOT_TOKEN, YOUR_GOD_CHAT_ID, and YOUR_ALLOWED_GROUP_ID with your Telegram bot token, your God chat ID (the Telegram user ID who can use all commands), and the allowed group ID where the bot will be functional.

### 🔄 Install as a Service
1. Create a new service file sysutilitybot.service:
```
sudo nano /etc/systemd/system/sysutilitybot.service
```
Add the following content to the sysutilitybot.service file:
```
[Unit]
Description=SysUtilityBot Telegram Bot
After=network.target

[Service]
User=your_username  # Replace 'your_username' with your system username
WorkingDirectory=/path/to/SysUtilityBot  # Replace '/path/to/SysUtilityBot' with the actual path
ExecStart=/usr/bin/python3.10 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```
Save and close the file (Ctrl + X, Y, Enter).

2. Reload systemd to recognize the new service:
```
sudo systemctl daemon-reload
```
3. Enable and start the SysUtilityBot service:
```
sudo systemctl enable sysutilitybot.service
sudo systemctl start sysutilitybot.service
```
Verify that the service is running:
```
sudo systemctl status sysutilitybot.service
```
Now, SysUtilityBot is set up as a service and will start automatically on system boot.

## 🕹️ Usage
Interact with the bot in your Telegram chat. You can use the following commands:

Commands for [All] Users:

- ℹ️ `/start` - Start the bot
- 🆔 `/id` - Get the chat ID (works in private chats, groups, and channels)

Commands for [Users] in the Allowed Group (Regular Users):

- ℹ️ `/start` - Start the bot
- 📚 `/help` - This Help Menu
- ℹ️ `/info` - Get system information
- 🆔 `/id` - Get the chat ID (works in private chats, groups, and channels)

Commands for [Admins] in the Allowed Group:

- ℹ️ `/start` - Start the bot
- 📚 `/help` - This Help Menu
- ℹ️ `/info` - Get system information
- 🆔 `/id` - Get the chat ID (works in private chats, groups, and channels)
- 💻 `/cmd <command>` - Execute a command on the server (limited)
- 👤🆕 `/add_user <user_id>` - Add a user ID to the user list
- 👤❌ `/remove_user <user_id>` - Remove a user ID from the user list
- 🔑🆕 `/add_admin <user_id>` - Add a user ID to the admin list
- 🔑❌ `/remove_admin <user_id>` - Remove a user ID from the admin list
- 📋 `/list_user` - List user IDs
- 📋 `/list_admin` - List admin IDs
- 🔄 `/update` - Update the system

Commands for the Super Admin (GOD user):
Available commands for GOD user in private messages

- ℹ️ `/start` - Start the bot
- 💤 `/reboot` - Rebooting the bot/server
- 📚 `/help` - This Help Menu
- ℹ️ `/info` - Get system information
- 🆔 `/id` - Get the chat ID (works in private chats, groups, and channels)
- 💻 `/cmd <command>` - Execute any shell command on the system without restrictions.
- 👤🆕 `/add_user <user_id>` - Add a user ID to the user list
- 👤❌ `/remove_user <user_id>` - Remove a user ID from the user list
- 🔑🆕 `/add_admin <user_id>` - Add a user ID to the admin list
- 🔑❌ `/remove_admin <user_id>` - Remove a user ID from the admin list
- 📋 `/list_user` - List user IDs
- 📋 `/list_admin` - List admin IDs
- 🔄 `/update` - Update the system

Note: The commands available to each user level are based on their access privileges. The bot's functionality is restricted to ensure system security and prevent unauthorized use.
> GOD HELP Menu

![](https://raw.githubusercontent.com/r0xd4n3t/SysUtilityBot/main/img/god.png)

**Contributions**

Contributions to SysUtilityBot are welcome! If you find any issues or have ideas for improvements, feel free to open an issue or submit a pull request.

Happy botting! 🤖
