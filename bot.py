# Standard Library Imports
import json
import os
import re
import subprocess
import time
from datetime import datetime, timedelta
from typing import List, Optional

# External Library Imports
import html
import psutil
import shlex
from telegram import Bot, Update, Chat, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def load_config():
    with open("config.json", "r") as file:
        return json.load(file)

def save_config(config):
    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)

config = load_config()
god_chat_id = config["god_chat_id"]

def greet_on_startup(bot: Bot, god_chat_id: int) -> None:
    bot.send_message(chat_id=god_chat_id, text="👋 I'm back!")

# Define a function to handle the API calls and retry on NetworkError
def safe_send_message(bot, chat_id, text, parse_mode=None):
    retries = 3
    for i in range(retries):
        try:
            return bot.send_message(chat_id, text, parse_mode=parse_mode)
        except telegram.error.NetworkError as e:
            if i == retries - 1:
                raise e
            else:
                time.sleep(1)  # Wait for 1 second before retrying

# SPY PM
def log_private_message(update: Update, context: CallbackContext) -> None:
    chat: Chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        user_id = update.message.from_user.id
        username = update.message.from_user.username or "Unknown"
        message_text = update.message.text

        log_message = f"[🕵️Spy] user: {user_id} @{username} send private Message: {message_text}"
        
        # Send the log to the destination chat
        safe_send_message(context.bot, god_chat_id, log_message)

# SPY CMD
def log_command(update: Update, context: CallbackContext) -> None:
    chat: Chat = update.effective_chat
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Unknown"
    message_text = update.message.text

    log_message = f"[🕵️Spy] user: {user_id} @{username} sent a command: {message_text}"
    
    # Send the log to the destination chat
    safe_send_message(context.bot, god_chat_id, log_message)

def reboot_system():
    try:
        subprocess.run(["sudo", "reboot"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while rebooting the system: {e}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")

# Command handler for /reboot in private messages
def reboot(update: Update, _: CallbackContext) -> None:
    if update.message.from_user.id == god_chat_id:
        # Send countdown message
        update.message.reply_text("💤 Rebooting in 3 seconds...")
        time.sleep(1)
        update.message.reply_text("💤 Rebooting in 2 seconds...")
        time.sleep(1)
        update.message.reply_text("💤 Rebooting in 1 second...")
        time.sleep(1)

        # Reboot the system using the safer method
        reboot_system()

    else:
        update.message.reply_text("⚠️ You are not authorized to use this command. ⚠️")

# Command handler for /start
def start(update: Update, _: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_first_name = update.message.from_user.first_name
    user_nickname = update.message.from_user.username

    # Check if the message is from a group and if it's the allowed group
    if update.message.chat.type == "group" and update.message.chat.id == config["allowed_group"]:
        # Greet users in the allowed group with their Telegram nickname or first name
        update.message.reply_text(f'👋😊 Hello, {"@" + user_nickname if user_nickname else user_first_name}! I am your server bot. Use /help within the permitted group to see available commands.')
    elif update.message.chat.type == "private":
        # Greet users in private messages with their Telegram nickname or first name
        update.message.reply_text(f'👋😊 Hello, {"@" + user_nickname if user_nickname else user_first_name}! I am your server bot. Use /help within the permitted group to see available commands.')
    else:
        # For users in other groups, check if they are authorized (admin or user)
        if user_id in config["admin_ids"] or user_id in config["user_ids"]:
            # Greet authorized users with their Telegram nickname or first name
            update.message.reply_text(f'👋😊 Hello, {"@" + user_nickname if user_nickname else user_first_name}! I am your server bot. Use /help within the permitted group to see available commands.')
        else:
            # Notify unauthorized users that they are not allowed to use other commands
            update.message.reply_text(f'👋😊 Hello, {"@" + user_nickname if user_nickname else user_first_name}! I am your server bot. Use /help within the permitted group to see available commands.')

# Command handler for /help
def help_command(update: Update, _: CallbackContext) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    if update.message.chat.type == "private":
        if user_id == god_chat_id:
            help_text = (
                "🌟🤖 Welcome to the Bot - Help Menu! 🌟🤖\n\n"
                "Available commands for GOD user in private messages:\n"
                "ℹ️ /start - Start the bot\n"
                "💤 /reboot - Rebooting the bot/server\n"
                "📚 /help - This Help Menu\n"
                "ℹ️ /info - Get system information\n"
                "🆔 /id - Get the chat ID (works in private chats, groups, and channels)\n"
                "💻 /cmd <command> - Execute a command on the server\n"
                "👤🆕 /add_user <user_id> - Add a user ID to the user list\n"
                "👤❌ /remove_user <user_id> - Remove a user ID from the user list\n"
                "🔑🆕 /add_admin <user_id> - Add a user ID to the admin list\n"
                "🔑❌ /remove_admin <user_id> - Remove a user ID from the admin list\n"
                "📋 /list_user - List user IDs\n"
                "📋 /list_admin - List admin IDs\n"
                "🔄 /update - Update the system\n"
            )
            update.message.reply_text(help_text)
        else:
            update.message.reply_text("⚠️ The /help command is not allowed in private messages.")
        return

    help_text = "🌟🤖 Welcome to the Bot - Help Menu! 🌟🤖\n\n"

    if chat_id == config["allowed_group"]:
        if user_id in config["admin_ids"] or user_id == god_chat_id:
            help_text += (
                "Available commands for admin users:\n"
                "ℹ️ /start - Start the bot\n"
                "📚 /help - This Help Menu\n"
                "ℹ️ /info - Get system information\n"
                "🆔 /id - Get the chat ID (works in private chats, groups, and channels)\n"
                "💻 /cmd <command> - Execute a command on the server (limited)\n"
                "👤🆕 /add_user <user_id> - Add a user ID to the user list\n"
                "👤❌ /remove_user <user_id> - Remove a user ID from the user list\n"
                "🔑🆕 /add_admin <user_id> - Add a user ID to the admin list\n"
                "🔑❌ /remove_admin <user_id> - Remove a user ID from the admin list\n"
                "📋 /list_user - List user IDs\n"
                "📋 /list_admin - List admin IDs\n"
                "🔄 /update - Update the system\n"
            )
            update.message.reply_text(help_text)

        elif user_id in config["user_ids"]:
            help_text += (
                "Available commands for normal users:\n"
                "ℹ️ /start - Start the bot\n"
                "📚 /help - This Help Menu\n"
                "ℹ️ /info - Get system information\n"
                "🆔 /id - Get the chat ID (works in private chats, groups, and channels)\n"
            )
            update.message.reply_text(help_text)

        else:
            help_text += (
                "Available commands for public users:\n"
                "ℹ️ /start - Start the bot\n"
                "🆔 /id - Get the chat ID (works in private chats, groups, and channels)\n"
            )
            update.message.reply_text(help_text)

    else:
        # For groups other than the allowed group, do not respond.
        pass

# Command handler for /update
def update_system(update: Update, _: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if update.message.chat.type == "private":
        if user_id == god_chat_id:
            try:
                update.message.reply_text("🔄 Updating system...")
                
                # Use subprocess.Popen to capture the output
                process = subprocess.Popen(
                    ["apt-get", "update", "-y"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                
                # Capture the output and error
                output, error = process.communicate()
                
                # Check if there was any error
                if process.returncode != 0:
                    update.message.reply_text(f"⚠️😕 Error occurred while updating the system: {error}")
                else:
                    # Send the captured output as the response
                    update.message.reply_text(f"<code>{output}</code>", parse_mode="HTML")

                process = subprocess.Popen(
                    ["apt", "upgrade", "-y"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                output, error = process.communicate()

                if process.returncode != 0:
                    update.message.reply_text(f"⚠️😕 Error occurred while updating the system: {error}")
                else:
                    update.message.reply_text(f"<code>{output}</code>", parse_mode="HTML")

                process = subprocess.Popen(
                    ["apt", "autoremove", "-y"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                output, error = process.communicate()

                if process.returncode != 0:
                    update.message.reply_text(f"⚠️😕 Error occurred while updating the system: {error}")
                else:
                    update.message.reply_text(f"<code>{output}</code>", parse_mode="HTML")

                process = subprocess.Popen(
                    ["apt", "autoclean", "-y"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                output, error = process.communicate()

                if process.returncode != 0:
                    update.message.reply_text(f"⚠️😕 Error occurred while updating the system: {error}")
                else:
                    update.message.reply_text(f"<code>{output}</code>", parse_mode="HTML")

                update.message.reply_text("🎉 System update completed.")
            except Exception as e:
                update.message.reply_text(f"⚠️😕 Error occurred while updating the system: {e}")
        else:
            update.message.reply_text("⚠️ The /update command is not allowed in private messages.")
    else:
        if user_id in config["admin_ids"] and update.message.chat.id == config["allowed_group"]:
            try:
                update.message.reply_text("🔄 Updating system...")
                
                # Use subprocess.Popen to capture the output
                process = subprocess.Popen(
                    ["apt-get", "update", "-y"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                
                # Capture the output and error
                output, error = process.communicate()
                
                # Check if there was any error
                if process.returncode != 0:
                    update.message.reply_text(f"⚠️😕 Error occurred while updating the system: {error}")
                else:
                    # Send the captured output as the response
                    update.message.reply_text(f"<code>{output}</code>", parse_mode="HTML")

                process = subprocess.Popen(
                    ["apt", "upgrade", "-y"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                output, error = process.communicate()

                if process.returncode != 0:
                    update.message.reply_text(f"⚠️😕 Error occurred while updating the system: {error}")
                else:
                    update.message.reply_text(f"<code>{output}</code>", parse_mode="HTML")

                process = subprocess.Popen(
                    ["apt", "autoremove", "-y"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                output, error = process.communicate()

                if process.returncode != 0:
                    update.message.reply_text(f"⚠️😕 Error occurred while updating the system: {error}")
                else:
                    update.message.reply_text(f"<code>{output}</code>", parse_mode="HTML")

                process = subprocess.Popen(
                    ["apt", "autoclean", "-y"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                output, error = process.communicate()

                if process.returncode != 0:
                    update.message.reply_text(f"⚠️😕 Error occurred while updating the system: {error}")
                else:
                    update.message.reply_text(f"<code>{output}</code>", parse_mode="HTML")

                update.message.reply_text("🎉 System update completed.")
            except Exception as e:
                update.message.reply_text(f"⚠️😕 Error occurred while updating the system: {e}")
        else:
            update.message.reply_text("⚠️ You are not authorized to perform this command ! ⚠️")

# Command handler for /add_user
def add_user(update: Update, context: CallbackContext) -> None:
    global config  # Declare config as a global variable to be able to modify it
    user_id = update.message.from_user.id
    
    if update.message.chat.type == "private":
        if user_id == god_chat_id:
            args = context.args
            if args:
                new_user_id = int(args[0])
                if new_user_id not in config["user_ids"]:
                    config["user_ids"].append(new_user_id)
                    save_config(config)
                    update.message.reply_text(f"🆕😄 User ID {new_user_id} added to the user list.")
                    # Reload the config after making changes
                    config = load_config()
                else:
                    update.message.reply_text("💔 User ID already exists in the user list.")
            else:
                update.message.reply_text("💡 Please use the command as follows: /add_user <user_id>")
        else:
            update.message.reply_text("⚠️ The /add_user command is not allowed in private messages.")
    elif update.message.chat.id == config["allowed_group"]:
        if user_id in config["admin_ids"]:
            args = context.args
            if args:
                new_user_id = int(args[0])
                if new_user_id not in config["user_ids"]:
                    config["user_ids"].append(new_user_id)
                    save_config(config)
                    update.message.reply_text(f"🆕😄 User ID {new_user_id} added to the user list.")
                    # Reload the config after making changes
                    config = load_config()
                else:
                    update.message.reply_text("💔 User ID already exists in the user list.")
            else:
                update.message.reply_text("💡 Please use the command as follows: /add_user <user_id>")
        else:
            update.message.reply_text("⚠️ You are not allowed to use this command ! ⚠️")
    else:
        update.message.reply_text("⚠️ You are not allowed to use this command in this group ! ⚠️")

# Command handler for /remove_user
def remove_user(update: Update, context: CallbackContext) -> None:
    global config  # Declare config as a global variable to be able to modify it
    
    if update.message.chat.type == "private":
        user_id = update.message.from_user.id
        if user_id == god_chat_id:
            args = context.args
            if args:
                user_id_to_remove = int(args[0])
                if user_id_to_remove in config["user_ids"]:
                    config["user_ids"].remove(user_id_to_remove)
                    save_config(config)
                    update.message.reply_text(f"✅ User ID {user_id_to_remove} removed from the user list.")
                    # Reload the config after making changes
                    config = load_config()
                else:
                    update.message.reply_text("❌ User ID not found in the user list.")
            else:
                update.message.reply_text("💡 Please use the command as follows: /remove_user <user_id>")
        else:
            update.message.reply_text("⚠️ The /remove_user command is not allowed in private messages.")
    elif update.message.chat.id == config["allowed_group"]:
        user_id = update.message.from_user.id
        if user_id in config["admin_ids"]:
            args = context.args
            if args:
                user_id_to_remove = int(args[0])
                if user_id_to_remove in config["user_ids"]:
                    config["user_ids"].remove(user_id_to_remove)
                    save_config(config)
                    update.message.reply_text(f"✅ User ID {user_id_to_remove} removed from the user list.")
                    # Reload the config after making changes
                    config = load_config()
                else:
                    update.message.reply_text("❌ User ID not found in the user list.")
            else:
                update.message.reply_text("💡 Please use the command as follows: /remove_user <user_id>")
        else:
            update.message.reply_text("⚠️ You are not allowed to use this command ! ⚠️")
    else:
        update.message.reply_text("⚠️ You are not allowed to use this command in this group ! ⚠️")

# Command handler for /add_admin
def add_admin(update: Update, context: CallbackContext) -> None:
    global config  # Declare config as a global variable to be able to modify it
    
    if update.message.chat.type == "private":
        user_id = update.message.from_user.id
        if user_id == god_chat_id:
            args = context.args
            if args:
                new_admin_id = int(args[0])
                if new_admin_id not in config["admin_ids"]:
                    config["admin_ids"].append(new_admin_id)
                    save_config(config)
                    update.message.reply_text(f"👤🔑 User ID {new_admin_id} added to the admin list.")
                    # Reload the config after making changes
                    config = load_config()
                else:
                    update.message.reply_text("🚫 User ID already exists in the admin list.")
            else:
                update.message.reply_text("💡 Please use the command as follows: /add_admin <user_id>")
        else:
            update.message.reply_text("⚠️ The /add_admin command is not allowed in private messages.")
    elif update.message.chat.id == config["allowed_group"]:
        user_id = update.message.from_user.id
        if user_id in config["admin_ids"]:
            args = context.args
            if args:
                new_admin_id = int(args[0])
                if new_admin_id not in config["admin_ids"]:
                    config["admin_ids"].append(new_admin_id)
                    save_config(config)
                    update.message.reply_text(f"👤🔑 User ID {new_admin_id} added to the admin list.")
                    # Reload the config after making changes
                    config = load_config()
                else:
                    update.message.reply_text("🚫 User ID already exists in the admin list.")
            else:
                update.message.reply_text("💡 Please use the command as follows: /add_admin <user_id>")
        else:
            update.message.reply_text("⚠️ You are not allowed to use this command ! ⚠️")
    else:
        update.message.reply_text("⚠️ You are not allowed to use this command in this group ! ⚠️")

# Command handler for /remove_admin
def remove_admin(update: Update, context: CallbackContext) -> None:
    global config  # Declare config as a global variable to be able to modify it
    
    if update.message.chat.type == "private":
        user_id = update.message.from_user.id
        if user_id == god_chat_id:
            args = context.args
            if args:
                admin_id_to_remove = int(args[0])
                if admin_id_to_remove in config["admin_ids"]:
                    config["admin_ids"].remove(admin_id_to_remove)
                    save_config(config)
                    update.message.reply_text(f"✨ User ID {admin_id_to_remove} removed from the admin list.")
                    # Reload the config after making changes
                    config = load_config()
                else:
                    update.message.reply_text("❓ User ID not found in the admin list.")
            else:
                update.message.reply_text("💡 Please use the command as follows: /remove_admin <user_id>")
        else:
            update.message.reply_text("⚠️ The /remove_admin command is not allowed in private messages.")
    elif update.message.chat.id == config["allowed_group"]:
        user_id = update.message.from_user.id
        if user_id in config["admin_ids"]:
            args = context.args
            if args:
                admin_id_to_remove = int(args[0])
                if admin_id_to_remove in config["admin_ids"]:
                    config["admin_ids"].remove(admin_id_to_remove)
                    save_config(config)
                    update.message.reply_text(f"✨ User ID {admin_id_to_remove} removed from the admin list.")
                    # Reload the config after making changes
                    config = load_config()
                else:
                    update.message.reply_text("❓ User ID not found in the admin list.")
            else:
                update.message.reply_text("💡 Please use the command as follows: /remove_admin <user_id>")
        else:
            update.message.reply_text("⚠️ You are not allowed to use this command ! ⚠️")
    else:
        update.message.reply_text("⚠️ You are not allowed to use this command in this group ! ⚠️")

def bytes_to_human_readable(bytes_value: int) -> str:
    """Convert bytes to a human-readable format."""
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0
    while bytes_value >= 1024 and index < len(suffixes) - 1:
        bytes_value /= 1024.0
        index += 1
    return f"{bytes_value:.2f} {suffixes[index]}"

def packets_to_human_readable(packets_value: int) -> str:
    """Convert packets to a human-readable format."""
    suffixes = ['packets', 'K packets', 'M packets', 'G packets', 'T packets']
    index = 0
    while packets_value >= 1000 and index < len(suffixes) - 1:
        packets_value /= 1000.0
        index += 1
    return f"{packets_value:.2f} {suffixes[index]}"

def get_who() -> str:
    try:
        output = subprocess.check_output(['w'], text=True, stderr=subprocess.STDOUT)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def get_last_10_logins() -> str:
    try:
        output = subprocess.check_output(['last', '-n', '10'], text=True, stderr=subprocess.STDOUT)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def list_open_ports() -> str:
    try:
        output = subprocess.check_output(['netstat', '-tuln'], text=True, stderr=subprocess.STDOUT)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

# Command handler for /info
def system_info(update: Update, _: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if update.message.chat.type == "private":
        if user_id == god_chat_id:
            update.message.reply_text("⏳ Please wait while I gather system information...")
            with os.popen('hostname') as hostname_output:
                hostname = hostname_output.read().strip()

            cpu_usage = psutil.cpu_percent(interval=1, percpu=False)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network_io = psutil.net_io_counters()
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time

            # Convert bytes to human-readable format
            bytes_sent_readable = bytes_to_human_readable(network_io.bytes_sent)
            bytes_recv_readable = bytes_to_human_readable(network_io.bytes_recv)

            # Convert packets to human-readable format
            packets_sent_readable = packets_to_human_readable(network_io.packets_sent)
            packets_recv_readable = packets_to_human_readable(network_io.packets_recv)

            # Get who, last 10 logins, open ports, and running processes
            who_info = get_who()
            last_logins = get_last_10_logins()
            open_ports = list_open_ports()
            
            # Construct the message
            message = (
                f"🏠 Hostname: {hostname}\n"
                f"💻 CPU Usage: {cpu_usage}%\n"
                f"🧠 Memory Usage: {memory.percent}%\n"
                f"💽 Disk Usage: {disk.percent}%\n"
                f"🌐 Network IO:\n"
                f"  📤 Bytes Sent: {bytes_sent_readable}\n"
                f"  📥 Bytes Received: {bytes_recv_readable}\n"
                f"  📦 Packets Sent: {packets_sent_readable}\n"
                f"  📦 Packets Received: {packets_recv_readable}\n"
                f"🚀 Boot Time: {datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"⏳ Uptime: {timedelta(seconds=int(uptime))}\n\n"
            )

            # Send the first part of the message
            update.message.reply_text(f"<code>{message}</code>", parse_mode="HTML")

            # Define a maximum message size
            max_message_size = 4000

            # Prepare the rest of the message parts
            additional_messages = [
                "👥 Who's logged in:\n",
                f"{who_info}\n\n",
                "🔒 Last 10 logins:\n",
                f"{last_logins}\n\n",
                "🔓 Open Ports:\n",
                f"{open_ports}\n\n"
            ]

            # Split the additional messages into parts that fit the maximum message size
            for additional_message in additional_messages:
                message_parts = [additional_message[i:i + max_message_size] for i in range(0, len(additional_message), max_message_size)]

                # Send each part of the message
                for part in message_parts:
                    update.message.reply_text(f"<code>{part}</code>", parse_mode="HTML")

        else:
            update.message.reply_text("⚠️ The /info command is not allowed in private messages.")
            return

    elif update.message.chat.id == config["allowed_group"]:
        if user_id in config["admin_ids"] or user_id in config["user_ids"]:
            update.message.reply_text("⏳ Please wait while I gather system information...")
            with os.popen('hostname') as hostname_output:
                hostname = hostname_output.read().strip()

            cpu_usage = psutil.cpu_percent(interval=1, percpu=False)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network_io = psutil.net_io_counters()
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time

            # Convert bytes to human-readable format
            bytes_sent_readable = bytes_to_human_readable(network_io.bytes_sent)
            bytes_recv_readable = bytes_to_human_readable(network_io.bytes_recv)

            # Convert packets to human-readable format
            packets_sent_readable = packets_to_human_readable(network_io.packets_sent)
            packets_recv_readable = packets_to_human_readable(network_io.packets_recv)

            # Get who, last 10 logins, open ports, and running processes
            who_info = get_who()
            last_logins = get_last_10_logins()
            open_ports = list_open_ports()
            
            # Construct the message
            message = (
                f"🏠 Hostname: {hostname}\n"
                f"💻 CPU Usage: {cpu_usage}%\n"
                f"🧠 Memory Usage: {memory.percent}%\n"
                f"💽 Disk Usage: {disk.percent}%\n"
                f"🌐 Network IO:\n"
                f"  📤 Bytes Sent: {bytes_sent_readable}\n"
                f"  📥 Bytes Received: {bytes_recv_readable}\n"
                f"  📦 Packets Sent: {packets_sent_readable}\n"
                f"  📦 Packets Received: {packets_recv_readable}\n"
                f"🚀 Boot Time: {datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"⏳ Uptime: {timedelta(seconds=int(uptime))}\n\n"
            )

            # Send the first part of the message
            update.message.reply_text(f"<code>{message}</code>", parse_mode="HTML")

            # Define a maximum message size
            max_message_size = 4000

            # Prepare the rest of the message parts
            additional_messages = [
                "👥 Who's logged in:\n",
                f"{who_info}\n\n",
                "🔒 Last 10 logins:\n",
                f"{last_logins}\n\n",
                "🔓 Open Ports:\n",
                f"{open_ports}\n\n"
            ]

            # Split the additional messages into parts that fit the maximum message size
            for additional_message in additional_messages:
                message_parts = [additional_message[i:i + max_message_size] for i in range(0, len(additional_message), max_message_size)]

                # Send each part of the message
                for part in message_parts:
                    update.message.reply_text(f"<code>{part}</code>", parse_mode="HTML")            

        else:
            update.message.reply_text("⚠️ You are not allowed to use this command ! ⚠️")
            return

    else:
        # For groups other than the allowed group, do not respond.
        pass

# Define the blacklist of commands that are not allowed to be executed
blacklist = ["reboot", "halt"]

# Command handler for /cmd
def run_command(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # Define a function to handle the API calls and retry on NetworkError
    def safe_send_message(bot, chat_id, text, parse_mode=None):
        retries = 3
        for i in range(retries):
            try:
                return bot.send_message(chat_id, text, parse_mode=parse_mode)
            except telegram.error.NetworkError as e:
                if i == retries - 1:
                    raise e
                else:
                    time.sleep(1)  # Wait for 1 second before retrying

    # Helper function to execute the command and capture the output
    def execute_command(command):
        try:
            # Check if any part of the command is in the blacklist
            command_parts = command.split()
            for part in command_parts:
                if part in blacklist and user_id != god_chat_id:
                    return "⚠️ This command is not allowed."

            # Escape special characters and quotes using shlex.quote for non-god users
            if user_id != god_chat_id:
                safe_command = shlex.quote(command)
            else:
                safe_command = command
            
            # Execute the command
            output = subprocess.check_output(safe_command, shell=True, text=True, stderr=subprocess.STDOUT)
            return output
        except subprocess.CalledProcessError as e:
            return f"Error: {e}"

    if user_id == god_chat_id:
        # Condition 3: Allow the command for the specific god_chat_id user
        args = context.args
        if args:
            command = " ".join(args)
            output = execute_command(command)

            # Escape special characters in the output message
            safe_output = html.escape(output)

            # Split the message into smaller parts if it exceeds the maximum size
            max_message_size = 4000
            message_parts = [safe_output[i:i + max_message_size] for i in range(0, len(safe_output), max_message_size)]

            # Send each part of the message
            for part in message_parts:
                safe_send_message(context.bot, update.message.chat_id, f"<code>{part}</code>", parse_mode="HTML")
        else:
            update.message.reply_text("💡 Please use the command as follows: /cmd <command>")
    elif update.message.chat.type == "private":
        # Condition 2: Prevent command execution in private messages
        update.message.reply_text("⚠️ The /cmd command is not allowed in private messages.")
    else:
        # Condition 1: Allow command execution for admins in group chats
        if user_id in config["admin_ids"]:
            args = context.args
            if args:
                command = " ".join(args)
                output = execute_command(command)

                # Escape special characters in the output message
                safe_output = html.escape(output)

                # Split the message into smaller parts if it exceeds the maximum size
                max_message_size = 4000
                message_parts = [safe_output[i:i + max_message_size] for i in range(0, len(safe_output), max_message_size)]

                # Send each part of the message
                for part in message_parts:
                    safe_send_message(context.bot, update.message.chat_id, f"<code>{part}</code>", parse_mode="HTML")
            else:
                update.message.reply_text("💡 Please use the command as follows: /cmd <command>")
        else:
            update.message.reply_text("⚠ You are not allowed to use this command ! ⚠️")

# Command handler for /list_admin
def list_admin(update: Update, _: CallbackContext) -> None:
    if update.message.chat.type == "private":
        user_id = update.message.from_user.id
        if user_id == god_chat_id:
            admin_ids_list = "\n".join(str(admin_id) for admin_id in config["admin_ids"])
            update.message.reply_text(f"<code>{admin_ids_list}</code>", parse_mode="HTML")
        else:
            update.message.reply_text("⚠ The /list_admin command is not allowed in private messages.")
    elif update.message.chat.id == config["allowed_group"]:
        user_id = update.message.from_user.id
        if user_id in config["admin_ids"]:
            admin_ids_list = "\n".join(str(admin_id) for admin_id in config["admin_ids"])
            update.message.reply_text(f"<code>{admin_ids_list}</code>", parse_mode="HTML")
        else:
            update.message.reply_text("⚠ You are not allowed to use this command ! ⚠️")
    else:
        update.message.reply_text("⚠️ You are not allowed to use this command in this group ! ⚠️")

# Command handler for /list_user
def list_user(update: Update, _: CallbackContext) -> None:
    if update.message.chat.type == "private":
        user_id = update.message.from_user.id
        if user_id == god_chat_id:
            user_ids_list = "\n".join(str(user_id) for user_id in config["user_ids"])
            if user_ids_list:
                update.message.reply_text(f"<code>{user_ids_list}</code>", parse_mode="HTML")
            else:
                update.message.reply_text("🔍 No user IDs found.")
        else:
            update.message.reply_text("⚠ The /list_user command is not allowed in private messages.")
    elif update.message.chat.id == config["allowed_group"]:
        user_id = update.message.from_user.id
        if user_id in config["admin_ids"]:
            user_ids_list = "\n".join(str(user_id) for user_id in config["user_ids"])
            if user_ids_list:
                update.message.reply_text(f"<code>{user_ids_list}</code>", parse_mode="HTML")
            else:
                update.message.reply_text("🔍 No user IDs found.")
        else:
            update.message.reply_text("⚠ You are not allowed to use this command ! ⚠️")
    else:
        update.message.reply_text("⚠️ You are not allowed to use this command in this group ! ⚠️")

# Improved command handler for /id
def get_id(update: Update, _: CallbackContext) -> None:
    chat = update.effective_chat
    update.message.reply_text(f"😊 This is a {chat.type}. ID: {chat.id}")

def main():
    updater = Updater(config["telegram_token"])
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("update", update_system))
    dispatcher.add_handler(CommandHandler("add_user", add_user, pass_args=True))
    dispatcher.add_handler(CommandHandler("remove_user", remove_user, pass_args=True))
    dispatcher.add_handler(CommandHandler("add_admin", add_admin, pass_args=True))
    dispatcher.add_handler(CommandHandler("remove_admin", remove_admin, pass_args=True))
    dispatcher.add_handler(CommandHandler("info", system_info))
    dispatcher.add_handler(CommandHandler("cmd", run_command, pass_args=True))
    dispatcher.add_handler(CommandHandler("list_admin", list_admin))
    dispatcher.add_handler(CommandHandler("list_user", list_user))
    dispatcher.add_handler(CommandHandler("id", get_id))
    dispatcher.add_handler(CommandHandler("reboot", reboot))
    dispatcher.add_handler(MessageHandler(Filters.chat_type.private & ~Filters.command, log_private_message))
    dispatcher.add_handler(MessageHandler(Filters.command, log_command, pass_user_data=True))


    updater.start_polling()
    # Greet the god on startup
    greet_on_startup(updater.bot, god_chat_id)
    updater.idle()

if __name__ == "__main__":
    main()

