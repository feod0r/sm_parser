#%config Completer.use_jedi = False
import asyncio
from operator import itemgetter

from flask import Flask
import json
import pymongo
import requests
import re
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from datetime import datetime
import logging

from telethon import TelegramClient
from telethon import functions, types

from GrabSM import GrabSM

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

config = json.load(open('../config.json', encoding="utf-8"))

blacklist = []

f = open('../data/black.list', 'r', encoding="utf-8")
blacklist = f.read().split('\n')
f.close()


#  d888b  d8888b. db    db d8888b. d8888b. d88888b d8888b.       .o88b. db       .d8b.  .d8888. .d8888.
# 88' Y8b 88  `8D 88    88 88  `8D 88  `8D 88'     88  `8D      d8P  Y8 88      d8' `8b 88'  YP 88'  YP
# 88      88oobY' 88    88 88oooY' 88oooY' 88ooooo 88oobY'      8P      88      88ooo88 `8bo.   `8bo.
# 88  ooo 88`8b   88    88 88~~~b. 88~~~b. 88~~~~~ 88`8b        8b      88      88~~~88   `Y8b.   `Y8b.
# 88. ~8~ 88 `88. 88b  d88 88   8D 88   8D 88.     88 `88.      Y8b  d8 88booo. 88   88 db   8D db   8D
#  Y888P  88   YD ~Y8888P' Y8888P' Y8888P' Y88888P 88   YD       `Y88P' Y88888P YP   YP `8888Y' `8888Y'
#
#


# d88888b db       .d8b.  .d8888. db   dD
# 88'     88      d8' `8b 88'  YP 88 ,8P'
# 88ooo   88      88ooo88 `8bo.   88,8P
# 88~~~   88      88~~~88   `Y8b. 88`8b
# 88      88booo. 88   88 db   8D 88 `88.
# YP      Y88888P YP   YP `8888Y' YP   YD
#
#
    

    
app = Flask(__name__)

sn = GrabSM()

sn.collect_links()

scheduler = BackgroundScheduler()
scheduler.add_job(func=sn.collect_links, trigger="interval", seconds=300)
scheduler.start()

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/size')
def size():
    return str(sn.vkPool.size())

@app.route('/take')
def take():    
    if sn.vkPool.size() == 0:
        return "Err_empty_list"
    
    post = sn.vkPool.take()
    if post != "Err_empty_list":
        post["_id"] = None
        post.pop('_id', None)
    return json.dumps(post, ensure_ascii=False) #, ensure_ascii=True)

@app.route('/taketen')
def taketen():    
    if sn.vkPool.size() == 0 and sn.vkPool.size() < 10:
        return "Err_empty_list"
    ans = []
    for i in range(10):   
        post = sn.vkPool.take()
        if post != "Err_empty_list":
            post["_id"] = None
            post.pop('_id', None)
            ans.append(post)
    return json.dumps(ans, ensure_ascii=False)#, ensure_ascii=True)

@app.route('/take100')
def take100():    
    if sn.vkPool.size() == 0 and sn.vkPool.size() < 100:
        return "Err_empty_list"
    ans = []
    for i in range(100):   
        post = sn.vkPool.take()
        if post != "Err_empty_list":
            post["_id"] = None
            post.pop('_id', None)
            ans.append(post)
    return json.dumps(ans, ensure_ascii=False)#, ensure_ascii=True)







# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
