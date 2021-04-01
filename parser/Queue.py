#  .d88b.  db    db d88888b db    db d88888b
# .8P  Y8. 88    88 88'     88    88 88'
# 88    88 88    88 88ooooo 88    88 88ooooo
# 88    88 88    88 88~~~~~ 88    88 88~~~~~
# `8P  d8' 88b  d88 88.     88b  d88 88.
#  `Y88'Y8 ~Y8888P' Y88888P ~Y8888P' Y88888P
#
#
from datetime import datetime
import json


class Queue:
    def __init__(self):
        self.items = []
        self.lock = False

    def is_empty(self):
        return self.items == []

    def clear(self):
        self.items = []

    def insert(self, item):
        in_collection = False
        f = open('../data/black.list', 'r', encoding="utf-8")
        global blacklist
        blacklist = f.read().split('\n')
        f.close()

        bl = blacklist
        if str(item.get('owner_id', 0)) in bl:
            print(datetime.now().strftime("[%D %H:%M:%S]"), '[Blacklisted]', item.get('owner_id', 0))
            return False

        for i in self.items:
            if item['se'] == 'v':
                if item['text'].lower().find(' сош ') != -1:
                    in_collection = True
                    # print(item['text'])
                if ((item.get('owner_id', '') == i.get('owner_id', '')) and (item['id'] == i['id'])) or (
                        item['text'][:125] == i['text'][:125]):
                    # print(json.dump(item, open('vk.json','w')))
                    in_collection = True
            if item['se'] == 't':
                if ((item.get('peer_id', '') == i.get('peer_id', '')) and (item['id'] == i['id'])) or (
                        item['text'][:125] == i['text'][:125]):
                    in_collection = True
                    # print(json.dump(item, open('tg.json', 'w')))
        if not in_collection:
            self.items.insert(0, item)

            return True
        else:
            return False

    def take(self):
        #         if not self.lock:
        return self.items.pop()

    #         return('Err_empty_list')

    def size(self):
        if not self.lock:
            return len(self.items)
        return 0

    def protect(self):
        self.lock = True

    def free(self):
        self.lock = False
