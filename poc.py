#!/usr/bin/env python3

import sys, time, telepot

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    show_keyboard = { 'keyboard':
                      [["Talk",        "Go North",      "Attack"  ],
                       ["Go West",     "Look",          "Go East" ],
                       ["Objects",     "Go South",      "Help",   ]] }

    bot.sendMessage(chat_id, "What do you want to do?", reply_markup=show_keyboard)



TOKEN='233755263:AAG6WCx7CWThTA-RppuDKs2j3hq9z15SPGY'

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print("Listening...")

while True:
    time.sleep(10)
    bot.sendMessage(167773515, "Random message from the MUD...")
    

