from transformers import BertTokenizer, BertConfig, BertForSequenceClassification, AdamW, PretrainedConfig
from transformers import get_linear_schedule_with_warmup
from pymorphy2 import MorphAnalyzer
import numpy as np
import pandas as pd
from nltk.tokenize import word_tokenize
import nltk
from tqdm import tqdm
import re
from tensorflow.keras.preprocessing.sequence import pad_sequences
import torch
import time

import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram

 #   _____             __ _       
 #  / ____|           / _(_)      
 # | |     ___  _ __ | |_ _  __ _ 
 # | |    / _ \| '_ \|  _| |/ _` |
 # | |___| (_) | | | | | | | (_| |
 #  \_____\___/|_| |_|_| |_|\__, |
 #                           __/ |
 #                          |___/ 

config = json.load(open('../config.json'))

bot = telegram.Bot(config['tgToken'])



nltk.download('stopwords')
from nltk.corpus import stopwords 
nltk.download('punkt')

 #                             _              _                      _    
 #                            | |            | |                    | |   
 #  _ __   ___ _   _ _ __ __ _| |  _ __   ___| |___      _____  _ __| | __
 # | '_ \ / _ \ | | | '__/ _` | | | '_ \ / _ \ __\ \ /\ / / _ \| '__| |/ /
 # | | | |  __/ |_| | | | (_| | | | | | |  __/ |_ \ V  V / (_) | |  |   < 
 # |_| |_|\___|\__,_|_|  \__,_|_| |_| |_|\___|\__| \_/\_/ \___/|_|  |_|\_\
                                                                        
                                                                        

def get_tokens(seqs):
    
    # очистка
    for ind, seq in enumerate(seqs):
        seq = re.sub(r"http\S+", "", seq)
        seq = re.sub(r"http", "", seq)
        seq = re.sub(r"@\S+", "", seq)
        seq = re.sub(r"#(\w+)", "", seq)
        seq = re.sub(r"[^A-Za-zА-Яа-яё0-9\.\!\?\...]", " ", seq)
        seq = re.sub(r"[a-zа-я0-9]+\.[a-zа-я0-9]+\.*[a-zа-я0-9]*", "", seq)
        seq = re.sub(r"id\w+", "", seq)
        seq = re.sub(r"\@", "at", seq)
        seqs[ind] = seq
    
    # лемматизация и тоенизация
    X = []
    for seq in tqdm(seqs):
        new_seq = ["[CLS]"]
        for word in word_tokenize(seq):
            if word == '.':
                new_seq.append('[SEP]')
            elif '.' in word or len(re.findall(r'[0-9]+', word)) > 0:
                pass
            elif word not in russina_stop_words and word not in usa_stop_words:
                new_seq.append(pymorphy2_analyzer.parse(word)[0].normal_form)

        if new_seq[-1] != '[SEP]':
            new_seq.append('[SEP]')
        X.append(new_seq)

    # паддинги

    input_ids = pad_sequences([tokenizer.convert_tokens_to_ids(txt) for txt in X],
                maxlen=MAX_LEN, dtype="long", truncating="post", padding="post", value=3)

    # attention masks
    attention_masks = []
    for sent in input_ids:
        att_mask = [int(token_id != 3) for token_id in sent]
        # Store the attention mask for this sentence.
        attention_masks.append(att_mask)
        
        
    return torch.tensor(input_ids), torch.tensor(attention_masks)




pymorphy2_analyzer = MorphAnalyzer()
russina_stop_words = stopwords.words('russian')
usa_stop_words = stopwords.words('english')
tokenizer = BertTokenizer.from_pretrained('./vocab.txt')
MAX_LEN = 128
load_path = './bert_structv2'
bert = BertForSequenceClassification.from_pretrained(str(load_path))

# seqs = 'Молодежная политика в моложежном вузе'

def predict(text):
    if not isinstance(text, list):
        text = [text]
    X, attention_masks = get_tokens(text)

    # пробуем
    bert.eval()
    preds = bert(X, 
        token_type_ids=None, 
        attention_mask=attention_masks)
    if not isinstance(text, list):
        return(np.argmax(preds[0].detach().numpy(), axis=1).flatten()[0])
    else:
        return(np.argmax(preds[0].detach().numpy(), axis=1).flatten())

 #                  _              _             _      
 #                 | |            | |           (_)     
 #  _ __   ___  ___| |_ ___ _ __  | | ___   __ _ _  ___ 
 # | '_ \ / _ \/ __| __/ _ \ '__| | |/ _ \ / _` | |/ __|
 # | |_) | (_) \__ \ ||  __/ |    | | (_) | (_| | | (__ 
 # | .__/ \___/|___/\__\___|_|    |_|\___/ \__, |_|\___|
 # | |                                      __/ |       
 # |_|                                     |___/        

def postTg(post, pred):
    file = open('../data/predictLog.csv', 'a', encoding="utf-8")
    trimmed_post = post['text'][:150]
    trimmed_post = trimmed_post.replace(';', '').replace('\n', '').replace('\r','').replace('\f', '').replace('"', '')
    trimmed_post = trimmed_post.replace('\\', '').replace('\"', '')
    file.write(str(pred) + ';' + trimmed_post+ ';'+ post['wallUrl'] + '\n')
    file.close()


    if pred:
        # search engine/index of post/ owner of post
        peer_id = post.get('peer_id', 0)
        payload = '{}/{}/{}'.format(post['se'], post['id'], post.get('owner_id', peer_id))
        # print(payload)

        datap = {'r':'+','i': payload, 'c':[0,0,0,0,0]}
        datad = {'r':'d','i': payload, 'c':[0,0,0,0,0]}
        datan = {'r':'-','i': payload, 'c':[0,0,0,0,0]}
        datar = {'r':'r','i': payload, 'c':[0,0,0,0,0]}
        datab = {'r':'b','i': payload, 'c':[0,0,0,0,0]}

        keyboard = [
            [
                InlineKeyboardButton("✅", callback_data=json.dumps(datap).replace(' ','')),
                InlineKeyboardButton("🗑", callback_data=json.dumps(datad).replace(' ','')),
                InlineKeyboardButton("❌", callback_data=json.dumps(datan).replace(' ','')),
            ],
            [
                InlineKeyboardButton("💾", callback_data=json.dumps(datar).replace(' ','')),
                InlineKeyboardButton("🏴‍☠️", callback_data=json.dumps(datab).replace(' ',''))
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            text = '[{}][{}]\n{}\n{}'.format( post['se'], post['query'], post['text'][:125],post['wallUrl'])
        except Exception as e:
            text = ''
            print(e)

        bot.send_message(chat_id="@ch3rtest",text=text,reply_markup=reply_markup)


def totg():
    availible = int(requests.get("http://{}:5000/size".format(config['serverIp'])).text)
    if availible < 20 and availible != 0: 
        post = requests.get("http://{}:5000/take".format(config['serverIp'])).text
        if(post != 'Err_empty_list'):
            post = json.loads(post)
            pred = predict(post['text'])
            postTg(post, pred)
    elif availible != 0: 
        if availible > 110:
            post = requests.get("http://{}:5000/take100".format(config['serverIp'])).text
        else:
            post = requests.get("http://{}:5000/taketen".format(config['serverIp'])).text
        if(post != 'Err_empty_list'):
            post = json.loads(post)
            texts = []
            for item in post:
                texts.append(item['text'])
            pred = predict(texts)
            print(list(pred))
            total = 0
            for i in pred:
                if i:
                    total += 1
            for i, predres in enumerate(list(pred)):
                postTg(post[i], predres)
                time.sleep(0.05 * total)
            # data = {
            #     "chat_id":"@ch3rtest",
            #     "text":text
            # }
            # requests.post(tgLink,data)

 #                     _____                                       
 #                    |  __ \                                      
 #  _ __ _   _ _ __   | |__) | __ ___   ___ ___  ___ ___  ___  ___ 
 # | '__| | | | '_ \  |  ___/ '__/ _ \ / __/ _ \/ __/ __|/ _ \/ __|
 # | |  | |_| | | | | | |   | | | (_) | (_|  __/\__ \__ \  __/\__ \
 # |_|   \__,_|_| |_| |_|   |_|  \___/ \___\___||___/___/\___||___/
                                                                 



scheduler = BackgroundScheduler()
scheduler.add_job(func=totg, trigger="interval", seconds=2)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

    

try:
    # This is here to simulate application activity (which keeps the main thread alive).
    while True:
        time.sleep(2)
except (KeyboardInterrupt, SystemExit):
    # Not strictly necessary if daemonic mode is enabled but should be done if possible
    scheduler.shutdown() 
    # botProcess.terminate()

# start_time = time.time()
# print(predict(seqs[5]))
# print("--- %s seconds ---" % (time.time() - start_time))
