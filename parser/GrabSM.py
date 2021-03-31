import json
from datetime import datetime

import pymongo
import requests
import asyncio
from operator import itemgetter

from Queue import Queue
from telethon import TelegramClient
from telethon import functions, types

config = json.load(open('config.json'))

class GrabSM(object):
    def __init__(self):

        self.client = pymongo.MongoClient('localhost', 27017)
        self.db = self.client['mirea']
        self.series_collection = self.db['vk']

        self.vkposts = []
        self.requests = []

        self.newestPostVK = {}
        self.newestPostTG = {}
        self.iteration = 0

        self.vkPool = Queue()

        self.newestPostTG = json.load(open('newestPostTG.json', 'r'))
        self.newestPostVK = json.load(open('newestPostVK.json', 'r'))

        # отладка. ссылки сохранены в файл
        # self.links = json.load(open('links.json', 'r'))
        '''self.requests.append('мирэа отзывы')
        self.requests.append('мгупи отзывы')
        self.requests.append('митхт отзывы')'''

    def collect_links(self):
        # выводит прогресс выполнения запросов и количество добавленных строк с каждого ресурса
        # 8-903-111-11-10
        # добавить парсинг по социальным сетям вк фб и телеграм
        # живая лента по новым публикациям в сми
        f = open('req.txt', 'r')
        self.requests = f.read().split('\n')
        f.close()
        self.vkPool.protect()
        for q in self.requests:
            print(datetime.now().strftime("[%D %H:%M:%S]"),
                  "[TG] Post/Dup {}".format(self.search_tg(q, 100)).ljust(33, ' '), '| {}'.format(q))

        for q in self.requests:
            if not q in self.newestPostVK:
                self.newestPostVK[q] = 0
            print(datetime.now().strftime("[%D %H:%M:%S]"),
                  "[VK] Post/Dup {}".format(self.add_vk(self.vk_search(q,125),q)).ljust(33,' '), '| {}'.format(q))

        # if self.iteration == 0:
        #     self.vkPool.clear()
        self.iteration += 1
        self.vkPool.free()

        json.dump(self.newestPostTG, open('newestPostTG.json', 'w', encoding='utf8'), ensure_ascii=False)
        json.dump(self.newestPostVK, open('newestPostVK.json', 'w', encoding='utf8'), ensure_ascii=False)

    # db    db db   dD
    # 88    88 88 ,8P'
    # Y8    8P 88,8P
    # `8b  d8' 88`8b
    #  `8bd8'  88 `88.
    #    YP    YP   YD
    #
    #
    def vk_post_info(self, post):
        #         for i in vksearchs:
        wallUrl = 'https://vk.com/wall{}_{}'.format(post['owner_id'], post['id'])
        ownerUrl = ''
        if post['from_id'] < 0:
            ownerUrl = 'https://vk.com/club{}'.format(post['from_id'] * -1)
        else:
            ownerUrl = 'https://vk.com/id{}'.format(post['from_id'])
        return (wallUrl, ownerUrl)

    def add_vk(self, posts, query):
        added = 0
        duplicates = 0
        posts.reverse()

        f = open('black.list', 'r')
        global blacklist
        blacklist = f.read().split('\n')
        f.close()

        for post in posts:
            #             if not ([post['owner_id'],post['from_id']] in [[i['owner_id'],i['from_id']] for i in self.vkposts]):
            if post['date'] > self.newestPostVK[query]:
                self.newestPostVK[query] = post['date']
                if post['post_type'] == 'post' and post['text'] != '':
                    post['query'] = query
                    post['wallUrl'], post['ownerUrl'] = self.vk_post_info(post)
                    post['se'] = 'v'
                    # self.vk_log_db(post)
                    if not self.vkPool.insert(post):
                        duplicates += 1
                    added += 1
        return added, duplicates

    def vk_log_db(self, post):
        def insert_db(data):
            try:
                return self.series_collection.insert_one(data).inserted_id
            except:
                return ('some err')

        insert_db(post)

    def vk_search(self, request, count):
        postVK = {
            "q": request,
            "extended": 1,
            "count": count,
            'start_time': self.newestPostTG.get(request, 0)
        }
        return json.loads(requests.post("https://api.vk.com/method/newsfeed.search?" + config['vkSerKey'] +
                                        config['vkVer'], postVK).text)['response']['items']

    # d888888b d88888b db      d88888b  d888b  d8888b.  .d8b.  .88b  d88.
    # `~~88~~' 88'     88      88'     88' Y8b 88  `8D d8' `8b 88'YbdP`88
    #    88    88ooooo 88      88ooooo 88      88oobY' 88ooo88 88  88  88
    #    88    88~~~~~ 88      88~~~~~ 88  ooo 88`8b   88~~~88 88  88  88
    #    88    88.     88booo. 88.     88. ~8~ 88 `88. 88   88 88  88  88
    #    YP    Y88888P Y88888P Y88888P  Y888P  88   YD YP   YP YP  YP  YP
    #
    #
    def search_tg(self, request, count):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            with TelegramClient(config['username'], config['api_id'], config['api_hash']) as client:
                result = loop.run_until_complete(client(functions.messages.SearchGlobalRequest(
                    q=request,
                    filter=types.ChannelMessagesFilterEmpty(),
                    min_date=datetime.fromtimestamp(self.newestPostTG.get(request, 0)), #вырубить для работы фильтра по времени
                    max_date=0,
                    offset_rate=0,
                    offset_peer='username',
                    offset_id=0,
                    limit=count,
                    folder_id=0
                )))

                mes = []
                for i in result.to_dict()['messages']:
                    msg = {}
                    i['date'] = i['date'].timestamp()
                    msg['text'] = i['message']
                    msg['peer_id'] = i['peer_id']['channel_id']
                    msg['id'] = i['id']
                    msg['date'] = i['date']
                    msg['se'] = 't'
                    msg['query'] = request
                    link = loop.run_until_complete(client(functions.channels.ExportMessageLinkRequest(
                        channel=msg['peer_id'],
                        id=i['id']
                    )))

                    msg['wallUrl'] = link.to_dict()['link']

                    if msg['date'] > self.newestPostTG.get(request, 0):
                        mes.append(msg)

                    # if msg['date'] > self.newestPostTG.get(request, 0):
                    #     self.newestPostTG[request] = msg['date']

                sorted(mes, key=itemgetter('date'))
                if len(mes)>0:
                    self.newestPostTG[request] = mes[0]['date']

                dup = 0
                for i in mes:
                    if not self.vkPool.insert(i):
                        dup += 1
                return len(mes), dup
                # json.dump(mes, open('log/{}.json'.format(request.replace('/', ''), encoding='utf8'), 'w'),
                #           ensure_ascii=False)
        except Exception as e:
            print(e)
            print(datetime.now().strftime("[%D %H:%M:%S]"), "[TG] Error while searching")

    def username_tg(self,peer, id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # try:
        with TelegramClient(config['username']+'_c', config['api_id'], config['api_hash']) as client:
            result = loop.run_until_complete(client(functions.channels.ExportMessageLinkRequest(
                channel=peer,
                id=id
            )))
            # print(result.to_dict()['link'])
            return result.to_dict()['link']
        # except:
        #     return 'err'