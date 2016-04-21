#!/usr/bin/env python
import telegram
import sys
import logging
import pickledb
from config import *

bot = telegram.Bot(token=TelegramBotToken)
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler(LogFile)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

custom_keyboard = [[ 'Zabbix status' ]]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
try:
   textalert = sys.argv[3]
except:
   logger.error('No data in $3 stdin argument')
   textalert = 'telegram-sent.py error: No data in $3 stdin argument'
try:
   db = pickledb.load(DBFile, False)
except:
   logger.error("Can't open DBFile")
allchats = db.getall()
logger.info(textalert)
for chat in allchats:
    if db.get(chat) == 'valid':
        bot.sendMessage(chat_id=chat, text=textalert, reply_markup=reply_markup)
