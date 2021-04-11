import logging
import json
import threading
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import asyncio
import sys

sys.path.insert(1, '../')

from DbConnect import DbConnect
from telethon import TelegramClient
from telethon import functions, types
import telethon
config = json.load(open('../config.json', 'r', encoding="utf-8"))
bot = telegram.Bot(config['tgToken'])

themes = {}

filename = '../data/corrections.csv'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Доступные команды:\n'
                              '/ranging - классификация обучающей выборки\n'
                              '/subtg - подписаться на канал в телеграмм\n'
                              '/unstg - отписаться от канала в телеграмм\n'
                              '/listtg - список подписок телеграмм\n')

def changeReq(update: Update, context: CallbackContext) -> None:
    pass


def ranging(update: Update, context: CallbackContext) -> None:
    data = {
        'r': 'rS'
    }
    keyboard = [
        [
            InlineKeyboardButton("Начать", callback_data=json.dumps(data).replace(' ', '')),
        ],
    ]

    req = open('../data/req.txt', 'r', encoding="utf-8")
    req = req.read().split('\n')

    for q in req:
        themes[q.split(':')[0]] = 1


    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Здравствуй друг! Данная команда нужна для формирования обучающей выборки для нейронной '
                              'сети.\n Твоя задача- отвечать, удовлетворяет ли интересующему контексту текст, '
                              'или нет. Для большего понимания будет приведен запрос, по которому получен этот текст.',reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    data = json.loads(query.data)
    print(data)

    # data = {}
    if data.get('r') == 'rS' or data.get('r') == 'rA':
        if data.get('r') == 'rS':
            keyboard = []
            for key in themes.keys():
                datap = {
                    'r': 'rA',
                    't': key
                }
                keyboard.append([InlineKeyboardButton(key, callback_data=json.dumps(datap, ensure_ascii=False).replace(' ', ''))])

            # keyboard = [
            #     [
            #         InlineKeyboardButton("ИМПМО", callback_data=json.dumps(datap).replace(' ', '')),
            #     ],
            #     [
            #         InlineKeyboardButton("ИМПМО", callback_data=json.dumps(datap).replace(' ', '')),
            #     ],
            # ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text('Выберете тему:')
            query.edit_message_reply_markup(reply_markup=reply_markup)

        elif data.get('r') == 'rA':
            # `id`, `class`, `theme`, `query`, `text`, `link`
            datap = {
                'r': 'rA',
                't': data['t'][:6],
                'cor': '1'
            }
            db = DbConnect()
            if data.get('id', False):
                db.correct_class(data['id'], data['cor'])

            row = db.take(data['t'])[0]
            datap['id'] = row[0]

            datan = datap.copy()
            datan['cor'] = '0'

            datad = datap.copy()
            datad['cor'] = '-1'

            keyboard = [
                [
                    InlineKeyboardButton("✅", callback_data=json.dumps(datap, ensure_ascii=False).replace(' ', '')),
                    InlineKeyboardButton("пропуск", callback_data=json.dumps(datad, ensure_ascii=False).replace(' ', '')),
                    InlineKeyboardButton("❌", callback_data=json.dumps(datan, ensure_ascii=False).replace(' ', '')),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text=f"[{data['t']}][{row[3]}]\n{row[4]}")
            query.edit_message_reply_markup(reply_markup=reply_markup)
    else:
        data['s'] = data['i'].split('/')[0]
        data['o'] = data['i'].split('/')[2]
        data['i'] = data['i'].split('/')[1]

        # search engine/index of post/ owner of post
        print(data)
        text = vkPost(str(data['o']) + '_' + str(data['i']))

        if data['r'] == 'r':
            bot.send_message(chat_id="@Ch3rSav3", text=query.message.text)
            data['c'][3] = data['c'][3] + 1
            # query.edit_message_text(text=query.message.text + "\nСохранено в чатик с влажными постами 󠁮󠁧󠁿💾")

        if text != [] and data['r'] != 'r':
            text = text[0]['text']
            text = text.replace('\r', ' ')
            text = text.replace('\n', ' ')
            text = text.replace('\t', ' ')

            if data['r'] == "-":
                # query.edit_message_text(text=f"Пост помечен к удалению 📛")
                data['c'][2] = data['c'][2] + 1
                if text:
                    f = open(filename, "a", encoding="utf-8")
                    f.write('0;' + text.replace(';', '') + '\n')
                    f.close()
            elif data['r'] == "+":
                # query.edit_message_text(text=query.message.text + "\nПост помечен как желаемый 👍🏽")
                data['c'][0] = data['c'][0] + 1
                if text:
                    f = open(filename, "a", encoding="utf-8")
                    f.write('1;' + text + '\n')
                    f.close()
            elif data['r'] == 'd':
                query.delete_message()
            elif data['r'] == 'b':
                f = open('../data/black.list', "a", encoding="utf-8")
                f.write(str(data['o']) + '\n')
                f.close()
                # query.edit_message_text(text=f"Источник занесен в черный список ⬛️")
                data['c'][4] = data['c'][4] + 1
            else:
                query.edit_message_text(text=query.data)
        else:
            if data['r'] == "-" or data['r'] == "d":
                query.edit_message_text(text="\nСтраница скрыта пользователем ☣️")
            else:
                query.edit_message_text(text=query.message.text + "\nСтраница скрыта пользователем ☣️")
        # query.edit_message_text(text=f"Selected option: {query.data}")

        datap = {'r': '+', 'i': '{}/{}/{}'.format(data['s'], data['i'], data['o']), 'c': data['c']}
        datad = {'r': 'd', 'i': '{}/{}/{}'.format(data['s'], data['i'], data['o']), 'c': data['c']}
        datan = {'r': '-', 'i': '{}/{}/{}'.format(data['s'], data['i'], data['o']), 'c': data['c']}
        datar = {'r': 'r', 'i': '{}/{}/{}'.format(data['s'], data['i'], data['o']), 'c': data['c']}
        datab = {'r': 'b', 'i': '{}/{}/{}'.format(data['s'], data['i'], data['o']), 'c': data['c']}

        keyboard = [
            [
                InlineKeyboardButton('✅ +{}'.format(data['c'][0]) if data['c'][0] > 0 else '✅',
                                     callback_data=json.dumps(datap).replace(' ', '')),
                InlineKeyboardButton('🗑', callback_data=json.dumps(datad).replace(' ', '')),
                InlineKeyboardButton('❌ +{}'.format(data['c'][2]) if data['c'][2] > 0 else '❌',
                                     callback_data=json.dumps(datan).replace(' ', '')),
            ],
            [
                InlineKeyboardButton('💾 +{}'.format(data['c'][3]) if data['c'][3] > 0 else '💾',
                                     callback_data=json.dumps(datar).replace(' ', '')),
                InlineKeyboardButton('🏴‍☠️ +{}'.format(data['c'][4]) if data['c'][4] > 0 else '🏴‍☠️',
                                     callback_data=json.dumps(datab).replace(' ', ''))
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)


        if data['r'] != 'd':
            query.edit_message_reply_markup(reply_markup=reply_markup)


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Use /start to test this bot.")


def list_subs(update: Update, context: CallbackContext) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        with TelegramClient(config['username'], config['api_id'], config['api_hash']) as client:
            result = loop.run_until_complete(client(functions.messages.GetDialogsRequest(
                offset_date=0,
                offset_id=0,
                offset_peer='username',
                limit=0,
                hash=0,
                exclude_pinned=True,
                folder_id=0
            )))
            chats = []
            for i in result.to_dict()['chats']:
                chats.append(i['title'] + ' | ' + str(i['id']))
            print(result.to_dict()['chats'])
            update.message.reply_text('Список подписок:\n' + '\n'.join(chats))
    except:
        update.message.reply_text('[список подписок] возникла какая-то ошибка')


def subscribe_tg(update: Update, context: CallbackContext) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        with TelegramClient(config['username'], config['api_id'], config['api_hash']) as client:
            result = loop.run_until_complete(client(functions.channels.JoinChannelRequest(
                channel=context.args[0].replace('https://t.me/','')
            )))
            # print(result.to_dict()['chats'])
            update.message.reply_text('Успешло подписались на ' + result.to_dict()['chats'][0]['title'])
    except :
        update.message.reply_text('[подписка]не удалось найти канал с указанным названием')


def unsubscribe_tg(update: Update, context: CallbackContext) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        with TelegramClient(config['username'], config['api_id'], config['api_hash']) as client:
            result = loop.run_until_complete(client(functions.channels.LeaveChannelRequest(
                channel=context.args[0].replace('https://t.me/','')
            )))
            # print(result.stringify())
            update.message.reply_text('Отписались от ' + result.to_dict()['chats'][0]['title'])
    except :
        update.message.reply_text('[отписка]не удалось найти канал с указанным названием')


def vkPost(post):
    postVK = {
        "posts": post,
        "extended": 0
    }
    req = json.loads(
        requests.post("https://api.vk.com/method/wall.getById?" + config['vkSerKey'] + config['vkVer'], postVK).text)
    return req['response']


def runbot():
    updater = Updater(config['tgToken'])

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.dispatcher.add_handler(CommandHandler('subtg', subscribe_tg))
    updater.dispatcher.add_handler(CommandHandler('unstg', unsubscribe_tg))
    updater.dispatcher.add_handler(CommandHandler('listtg', list_subs))
    updater.dispatcher.add_handler(CommandHandler('ranging', ranging))


    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


runbot()

