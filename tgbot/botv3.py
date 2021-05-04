import logging
import json
import threading
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup
import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler, \
    MessageHandler, Filters
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
                              '/themes - редактирование списка запросов\n'
                              '/unstg - отписаться от канала в телеграмм\n'
                              '/listtg - список подписок телеграмм\n')
    context.user_data['test'] = 123
    print(context.user_data)


def changeReq(update: Update, context: CallbackContext) -> None:
    req = open('../data/req.txt', 'r', encoding="utf-8")
    req = req.read().split('\n')
    # print(context.user_data)

    for q in req:
        themes[q.split(':')[0]] = 1

    keyboard = []
    for key in themes.keys():
        datap = {
            'r': 'ct',
            't': key
        }
        keyboard.append(
            [InlineKeyboardButton(key, callback_data=json.dumps(datap, ensure_ascii=False).replace(' ', ''))])

    dataAdd = {
        'r': 'ct',
        't': 'ADD',
        'a': 'add'
    }
    keyboard.append(
        [InlineKeyboardButton('Добавить', callback_data=json.dumps(dataAdd, ensure_ascii=False).replace(' ', ''))])
    dataDel = {
        'r': 'ct',
        't': 'DEL',
        'a': 'del'
    }
    keyboard.append(
        [InlineKeyboardButton('Удалить', callback_data=json.dumps(dataDel, ensure_ascii=False).replace(' ', ''))])

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберете тему для редактирования:\n',reply_markup=reply_markup)


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


def read_req(theme):
    req = open('../data/req.txt', 'r', encoding="utf-8")
    rest = req.read().split('\n')
    req_arr = []
    for q in rest:
        if q!='':
            if q.split(':')[0] == theme:
                req_arr.append(q.split(':')[1])
    req.close()
    return req_arr


def add_req(theme, rest):
    req = open('../data/req.txt', 'r', encoding="utf-8")
    old = req.read().split('\n')
    req.close()
    req = open('../data/req.txt', 'w', encoding="utf-8")

    for row in old:
        # print(row.split(':')[0], row.split(':')[1], theme, rest, not ((row.split(':')[0] != theme) and (row.split(':')[1] != str(rest))))
        if row != '':
            if (not ((row.split(':')[0] == theme) and (row.split(':')[1] == str(rest)))):
                buf = f"{row.split(':')[0]}:{row.split(':')[1]}\n"
                req.write(buf)
    req.write(f"{theme}:{rest}")
    req.close()


def del_req(theme, rest):
    req = open('../data/req.txt', 'r', encoding="utf-8")
    old = req.read().split('\n')
    req.close()
    req = open('../data/req.txt', 'w', encoding="utf-8")
    for row in old:
        if not ((row.split(':')[0] == theme) and (row.split(':')[1] == str(rest))):
            req.write(f"{row.split(':')[0]}:{row.split(':')[1]}\n")
    req.close()


def del_theme(theme):
    req = open('../data/req.txt', 'r', encoding="utf-8")
    old = req.read().split('\n')
    req.close()
    req = open('../data/req.txt', 'w', encoding="utf-8")
    for row in old:
        if row.split(':')[0] != theme and row != '':
            req.write(f"{row.split(':')[0]}:{row.split(':')[1]}\n")
    req.close()


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    data = json.loads(query.data)
    print(data)
    reqCorr = ['+', '-', 'r', 'd', 'b']

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
    elif data['r'] in reqCorr:
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
    elif data['r'] == 'ct':
        context.user_data['theme'] = data.get('t', '')
        if data.get('t', '') == 'ADD' or data.get('t', '') == 'DEL':
            query.edit_message_text(text="Напишите тему:")
        else:
            query.edit_message_text(text="Выбрана тема " + data.get('t', ''))
            list_int_file = ''
            for n,i in enumerate(read_req(data.get('t', ''))):
                list_int_file = list_int_file + str(n) + ') ' + i + '\n'
            query.message.reply_text(text="Cписок текущих запросов\n" + list_int_file +
                                         "Напиши \"+запрос\" чтобы добавить тему\n"
                                         "Напиши \"-запрос\" или \"-id\" чтобы удалить тему")
    else:
        query.edit_message_text(text="another unregistered data of callback "
                                     "updater.dispatcher.add_handler(CallbackQueryHandler(button))")


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

def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.'
    )

    return ConversationHandler.END


def mess_handle(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    if user_data.get('theme') == 'DEL':
        update.message.reply_text('Удалено ' + update.message.text)
        del_theme(update.message.text)
        del context.user_data['theme']
    elif user_data.get('theme') == 'ADD':
        update.message.reply_text('Добавлена тема ' + update.message.text + '. необходимо добавить хотя бы 1 запрос.\n'
                                                                            'чтобы добавить запрос, напишите символ "+"'
                                                                            'и без пробелов сам запрос.')
        context.user_data['theme'] = update.message.text[:5]
        # del context.user_data['theme']
    elif user_data.get('theme', '') != '':
        if update.message.text[0] == '+':
            add_req(user_data.get('theme', ''), update.message.text[1:])
            update.message.reply_text(
                'В тему ' + context.user_data['theme'] + ' добавлен новый запрос: ' + update.message.text[1:])
        elif update.message.text[0] == '-':
            del_req(user_data.get('theme', ''), update.message.text[1:])
            update.message.reply_text(
                'Из темы ' + context.user_data['theme'] + ' удален запрос: ' + update.message.text[1:])
        else:
            update.message.reply_text('Нет управляющего символа для запроса. Сейчас выбрана тема: ' + context.user_data['theme'] )


def links_theme(update: Update, context: CallbackContext) -> int:
    db = DbConnect()
    db_themes = db.show_themes_links()

    query = 'Здравствуй, друг!\nВыбери тему, с которой ты хочешь работать (либо напиши новую):\n'
    for i in db_themes:
        query += str(i[0]) + "\n"
    update.message.reply_text(query)
    return 0


def links_link(update: Update, context: CallbackContext) -> int:

    context.user_data['link_theme'] = update.message.text
    query = f'Тему "{update.message.text}" запомнил.\n А теперь, укажите ссылку: '
    update.message.reply_text(query)
    print(context.user_data)
    return 1


def links_caption(update: Update, context: CallbackContext) -> int:

    context.user_data['link'] = update.message.text
    query = f'Ссылку "{update.message.text}" сохранил.\n Ей можно придумать описание: '
    update.message.reply_text(query)
    print(context.user_data)
    return 2


def links_final(update: Update, context: CallbackContext) -> int:
    db = DbConnect()
    db.insert_links(context.user_data.get('link'), update.message.text, context.user_data.get('link_theme'))
    query = f'Описание "{update.message.text}" сохранил.\n Конец'
    update.message.reply_text(query)
    return ConversationHandler.END


def runbot():
    updater = Updater(config['tgToken'])
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('links', links_theme)],
        states={
            0: [MessageHandler(Filters.text, links_link)],
            1: [MessageHandler(Filters.text, links_caption)],
            2: [MessageHandler(Filters.text, links_final)],
            # BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    updater.dispatcher.add_handler(conv_handler)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.dispatcher.add_handler(CommandHandler('subtg', subscribe_tg))
    updater.dispatcher.add_handler(CommandHandler('unstg', unsubscribe_tg))
    updater.dispatcher.add_handler(CommandHandler('listtg', list_subs))
    updater.dispatcher.add_handler(CommandHandler('ranging', ranging))
    updater.dispatcher.add_handler(CommandHandler('themes', changeReq))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, mess_handle))



    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


runbot()

