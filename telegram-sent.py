#!/usr/bin/env python
import telegram
import sys
import logging
import pickledb

###Variables###
TelegramBotToken='164444419:BBERDQsjJBG_lx8qPQsAFLDCMIc1XxhINlw'
DBFile='/opt/telegram-bot/telegram.db'
LogFile='/var/log/telegram.log'
###EndVariables###

bot = telegram.Bot(token=TelegramBotToken)
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler(LogFile)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

custom_keyboard = [[ 'Zabbix status', 'Unsubscribe' ]]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
text = 'Zabbix:\n' + sys.argv[3]
#text = sys.argv[3]
db = pickledb.load(DBFile, False)
allchats = db.getall()
logger.info(text)
for chat in allchats:
    if db.get(chat) == 'valid':
        bot.sendMessage(chat_id=chat, text=text, reply_markup=reply_markup)
