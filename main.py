import json
import logging
import threading
import time
from datetime import datetime

import config
import telebot

bot = telebot.TeleBot(config.TOKEN)

with open("users.json", encoding="utf-8") as js:
    users_data = json.load(js)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(message.chat.id, f"Hi, {message.from_user.first_name} {message.from_user.last_name} \n"
                                      f"I\'m <b>{bot.get_me().first_name}</b>,"
                                      f" bot that provides notifications and reminding about \n"
                                      f"<b>Oxygen level check</b>!\n"
                                      f"Type /set_start_now to set reminding \nevery %Interval_time% starting from current time\n"
                                      f"Type /set_remind_interval to set reminding time interval\n"
                                      f"Type /set_oxygen_level to set current oxygen level\n"
                                      f"Type /help for all commands.",
                                      parse_mode='html')


@bot.message_handler(commands=["help"])
def show_commands(message):
    bot.send_message(message.chat.id, "/start - Work start\n"
                                      "/set_start_now - set reminder from current time\n"
                                      "/set_remind_interval - set reminding interval\n"
                                      "/set_oxygen_level - set current oxygen level\n"
                                      "/help - show help\n"
                                      "/leave - turn off notifications\n")


@bot.message_handler(commands=["set_remind_interval"])
def set_remind_interval(message):

    if str(message.chat.id) in users_data:
        bot.send_message(message.chat.id, "Type correct interval time in minutes")
        bot.register_next_step_handler(message, set_interval)
    else:
        bot.send_message(message.chat.id, "You are not in users list!")

def set_interval(message):
    current_time = datetime.now().strftime("%H:%M:%S")
    temp = current_time.split(':')
    users_data[f"{message.chat.id}"]["remindInterval"] = message.text
    trigger_time = int(temp[0]) * 3600 + int(temp[1]) * 60 + int(temp[2]) + int(users_data[f"{message.chat.id}"]["remindInterval"]) * 60
    trigger_time = ('%02d:%02d:%02d' % (
        trigger_time // 3600, trigger_time % 3600 // 60, trigger_time % 3600 % 60))
    users_data[f"{message.chat.id}"]["triggerTime"] = trigger_time

    with open('users.json', 'w', encoding="utf-8") as js:
        json.dump(users_data, js)

    bot.send_message(message.chat.id, "Remind interval saved correctly!")

@bot.message_handler(commands=["set_start_now"])
def set_start_now(message):
    users_data[f"{message.chat.id}"] = {"startTime": "", "remindInterval": "", "triggerTime":"", "currentOxygenLvl": ""}
    if str(message.chat.id) in users_data:
        set_start(message)
    else:
        bot.send_message(message.chat.id, "You are not in users list!")

def set_start(message):
    users_data[f"{message.chat.id}"]["startTime"] = str(datetime.now().strftime("%H:%M:%S"))

    with open('users.json', 'w', encoding="utf-8") as js:
        json.dump(users_data, js)

    bot.send_message(message.chat.id, f"Start time saved correctly! {datetime.now().strftime('%H:%M:%S')}")

@bot.message_handler(commands=["set_oxygen_level"])
def set_oxygen_level(message):

    if str(message.chat.id) in users_data:
        bot.send_message(message.chat.id, "Type correct Oxygen value")
        bot.register_next_step_handler(message, set_oxygen)
    else:
        bot.send_message(message.chat.id, "You are not in users list!")

def set_oxygen(message):
    users_data[f"{message.chat.id}"]["currentOxygenLvl"] = message.text

    with open('users.json', 'w', encoding="utf-8") as js:
        json.dump(users_data, js)

    bot.send_message(message.chat.id, "Current oxygen level saved correctly!")


@bot.message_handler(commands=["leave"])
def leave(message):
    if str(message.chat.id) in users_data:
        users_data.pop(str(message.chat.id))

        with open('users.json', 'w', encoding="utf-8") as js:
            json.dump(users_data, js)

        bot.send_message(message.chat.id, "You turned off notifications successfully. \n"
                                          "To turn notifications ON press \n"
                                          "/set_start_now")
    else:
        bot.send_message(message.chat.id, "You are not in users list!")


def notify():
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        to_delete = []

        for user in users_data:
            if current_time == users_data[user]['triggerTime']:
                try:
                    bot.send_message(int(user), f"Time to send Oxygen current level!\n"
                                                f"Your last Oxygen level: {users_data[user]['currentOxygenLvl']}")
                    temp = current_time.split(':')
                    trigger_time = int(temp[0]) * 3600 + int(temp[1]) * 60 + int(temp[2]) + int(
                        users_data[user]["remindInterval"]) * 60
                    trigger_time = ('%02d:%02d:%02d' % (
                        trigger_time // 3600, trigger_time % 3600 // 60, trigger_time % 3600 % 60))
                    users_data[user]["triggerTime"] = trigger_time
                    with open('users.json', 'w', encoding="utf-8") as js:
                        json.dump(users_data, js)
                except telebot.apihelper.ApiTelegramException:
                    to_delete.append(user)

        for user in to_delete:
            users_data.pop(user)

            with open('users.json', 'w', encoding="utf-8") as js:
                json.dump(users_data, js)

        time.sleep(1)


thr = threading.Thread(target=notify)
thr.start()

while True:
        bot.polling(none_stop=True)
        logging.error(err)
        print("No internet connection.")