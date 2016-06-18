import telegram
import pickledb
from flask import Flask, request
from pyzabbix import ZabbixAPI
from config import *

app = Flask(__name__)
app.config['ASSETS_DEBUG'] = True
app.debug = True
bot = telegram.Bot(token=TelegramBotToken)

def zabbix_triggers():
    # The hostname at which the Zabbix web interface is available
    zapi = ZabbixAPI(ZabbixServerUrl)
    # Login to the Zabbix API
    zapi.login(ZabbixUsername, ZabbixPassword)
    # Get a list of all issues (AKA tripped triggers)
    triggers = zapi.trigger.get(only_true=1, skipDependent=1, monitored=1, active=1, output='extend', expandDescription=1, selectHosts=1)

    # Do another query to find out which issues are Unacknowledged
    unack_triggers = zapi.trigger.get(only_true=1, skipDependent=1, monitored=1, active=1, output='extend', expandDescription=1, selectHosts=1, withLastEventUnacknowledged=1)
    unack_trigger_ids = [t['triggerid'] for t in unack_triggers]
    for t in triggers:
        zabbixhost = zapi.host.get(hostids=int(t['hosts'][0]['hostid']))
        t['host']=zabbixhost[0]['host']
        t['unacknowledged'] = True if t['triggerid'] in unack_trigger_ids\
        else False
    return triggers


@app.route('/hook', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True))
        chat_id = str(update.message.chat.id)
        text = update.message.text.encode('utf-8')
        db = pickledb.load(DBFile, False)
        custom_keyboard = [[ 'Zabbix status' ]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        allchats = db.getall()
        if chat_id in allchats and db.get(chat_id) == 'valid':
            if text.lower() == 'zabbix status' or text.lower() == '/status':
                triggers = zabbix_triggers()
                haveproblems = None
                fullalerttext = 'Zabbix:\n'
                for t in triggers:
                    if int(t['value']) == 1:
                        haveproblems = True
                        alerttext=t['host'] + ' - ' + t['description']
                        if int(t['priority']) == 1:
                            fullalerttext = fullalerttext + alerttext.encode('utf-8') + ' - Information' + telegram.Emoji.SMILING_FACE_WITH_SUNGLASSES + '\n'
                        elif int(t['priority']) == 2:
                            fullalerttext = fullalerttext + alerttext.encode('utf-8') + ' - Warning' + telegram.Emoji.WORRIED_FACE + '\n'
                        elif int(t['priority']) == 3:
                            fullalerttext = fullalerttext + alerttext.encode('utf-8') + ' - Average' + telegram.Emoji.FACE_WITH_OPEN_MOUTH + '\n'
                        elif int(t['priority']) == 4:
                            fullalerttext = fullalerttext + alerttext.encode('utf-8') +  ' - High' + telegram.Emoji.FEARFUL_FACE + '\n'
                        elif int(t['priority']) == 5:
                            fullalerttext = fullalerttext + alerttext.encode('utf-8') +  ' - Disaster' + telegram.Emoji.FACE_SCREAMING_IN_FEAR + '\n'
                        else:
                            fullalerttext = fullalerttext + alerttext.encode('utf-8') + ' - Not classified' + telegram.Emoji.WINKING_FACE + '\n'
                if not haveproblems:
                    fullalerttext = fullalerttext + 'Everything is OK!' + telegram.Emoji.SMILING_FACE_WITH_SUNGLASSES
                bot.sendMessage(chat_id=chat_id, text=fullalerttext, reply_markup=reply_markup)
            elif text.lower() == 'unsubscribe' or text.lower == '/unsubscribe':
                db.rem(chat_id)
                db.dump()
                reply_markup = telegram.ReplyKeyboardHide()
                bot.sendMessage(chat_id=chat_id, text='You successfully unsubscribed!\nYou will not receive alerts from this bot.', reply_markup=reply_markup)
#            if text.lower() == '/start' or text.lower() == '/help':
            else:
                bot.sendMessage(chat_id=chat_id, text='List of bot commands:\n/status - show all alerts\n/unsubscribe - unsubscribe from this bot\n/help - list of bot commands', reply_markup=reply_markup)
        else:
            if chat_id in allchats and db.get(chat_id) == 'unauth':
                if text == ChatPassword:
                    db.set(chat_id, 'valid')
                    db.dump()
                    bot.sendMessage(chat_id=chat_id, text='You successfully authenticated. Now you will be receive alerts from zabbix.\nType /help to see all commands.', reply_markup=reply_markup)
                else:
                    bot.sendMessage(chat_id=chat_id, text='Wrong password. Please enter valid password')
            else:
                db.set(chat_id, 'unauth')
                db.dump()
                bot.sendMessage(chat_id=chat_id, text='Please enter password')
    return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook(WebHookUrl)
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return 'Work'

if __name__ == "__main__":
    try:
        app.run(debug=True)
    except Exception:
        app.logger.exception('Failed')
