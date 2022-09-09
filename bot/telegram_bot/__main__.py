import telebot
from telebot import types
import os
import requests
import time
from . import headlines
from . import query
import numpy as np
from pathlib import Path
import json
import pandas as pd


tb = telebot.TeleBot('5623203213:AAH7lof9-02ixyYrc4V4B02JYWjTWw8o6qY')

@tb.message_handler(commands=['start', 'go'])
def start_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [types.KeyboardButton("Отправить данные"),
             types.KeyboardButton("Часто задаваемые вопросы"),
            ]
    for item in items:
        markup.add(item)
    msg = tb.send_message(message.chat.id, f'*Добро пожаловать, {message.from_user.first_name}!*\n\n'+headlines.start,  reply_markup=markup, parse_mode= 'Markdown')
    tb.register_next_step_handler(msg, main_start)

def main_start(message):
    if message.text.strip() == 'Отправить данные':
        msg = tb.send_message(message.chat.id, f'Пожалуйста, прикрепите и отправьте мне файл с результатми вашего генома.', parse_mode= 'Markdown')
        path = os.path.join(os.path.dirname(__file__), 'guide.png')
        tb.send_photo(message.chat.id, photo=open(path, 'rb'))
    if message.text.strip() == "Часто задаваемые вопросы":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = [types.KeyboardButton("Отправить данные"),
                ]
        for item in items:
            markup.add(item)
        msg = tb.send_message(message.chat.id, headlines.question_answer, reply_markup=markup, parse_mode= 'Markdown')
        tb.register_next_step_handler(msg, main_start)

@tb.message_handler(content_types=['document'])
def handle_docs_photo(message):
    try:
        file_info = tb.get_file(message.document.file_id)
        downloaded_file = tb.download_file(file_info.file_path)  
        ts = time.time()
        path = Path(os.path.dirname(__file__)) / 'load_data'
        path.mkdir(exist_ok=True)
        src = path / f'{message.chat.id}_{ts}.txt'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        msg = tb.reply_to(message, "*Спасибо!*\n\n*Мой искусственный интелект начал обрабатывать информацию!*\n\n⚙️⚙️⚙️⚙️⚙️⚙️⚙️⚙️\n\n_Как только я закончу, я пришлю информацию моего анализа._", parse_mode= 'Markdown')
        process(message=msg, file_name=src)
    except Exception as e:
        msg = tb.reply_to(message, f'*Упс!*\n\nКажется в вашем файле проблемы! Проверьте точно ли вы загружаете нужный файл! {e}\n\n_По любым вопросам можно обратиться к моим разработчикам_\n@voronik1801', parse_mode= 'Markdown')
        tb.register_next_step_handler(msg, handle_docs_photo)

def process(message, file_name):
    snps = []
    with open(file_name) as f:
        for line in f.readlines():
            if line[0] == '#':
                continue
            tokens = line.split()
            if tokens[1] != '1':
                continue
            try:
                snp = {
                    'rs': int(tokens[0][2:]),
                    'genotype': tokens[3]
                }
                snps.append(snp)
            except ValueError:
                pass
    clinvar_dir = Path(os.path.dirname(__file__)) / '../data/clinvar_filtered.json'
    with open(clinvar_dir, 'r') as file:
        clinvar = json.load(file)

    clinvar_df = pd.DataFrame.from_records(clinvar)
    clinvar_df['rs_int'] = clinvar_df['rs_id'].apply(lambda x: x.isnumeric())
    clinvar_df = clinvar_df[clinvar_df['rs_int']].copy().drop('rs_int', axis=1)
    clinvar_df['rs'] = clinvar_df['rs_id'].astype(int)

    result = query.check_user_snps(snps, clinvar_df)

    df = pd.DataFrame.from_records(result)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [types.KeyboardButton("Отправить данные"),
             types.KeyboardButton("Часто задаваемые вопросы"),
            ]
    for item in items:
        markup.add(item)
    if len(df) > 0:
        # for rs in response:
        #     rs_for_check = rs['_source']['rs_id']
        #     tb.send_message(message.chat.id, f"_Мы обнаружили высокий риск развития болезни, ассоциированной с участком в геноме rs-{rs_for_check}_", parse_mode= 'Markdown')
        risks = []
        tb.send_message(message.chat.id, f"Мы обнаружили следующие риски:", parse_mode= 'Markdown')
        for _, row in df.iterrows():
            try:
                description = row["description"].replace('_', ' ')
                risk = f'RS{row["rs"]} - {description.split("|")[0].split(",")[0]}'
                tb.send_message(message.chat.id, risk, parse_mode= 'Markdown')
                
            except Exception:
                pass
        

        msg = tb.send_message(message.chat.id, "Вы можете проверить данные участки в лаборатории *Имя партнера*.\n\nПо промокоду *Deeploid* вы получите скидку в 10%", reply_markup=markup, parse_mode= 'Markdown')
    else:
        msg = tb.send_message(message.chat.id, "Мы не обнаружили никаких паталогийв вашем геноме.", reply_markup=markup, parse_mode= 'Markdown')
    tb.register_next_step_handler(msg, main_start)
    return



    result = []
    with open(file_name, 'r') as f:
        lines = [line for line in f if not line.startswith("#")]
        filtered = "".join(lines)
    filtered = filtered.split('\n')
    for line in filtered:
        result.append(line.split('\t'))
    rs_id = [el[0].replace('rs','') for el in result]
    rs_id = np.random.choice(rs_id, 700, replace=False)
    req_link = f'http://176.9.183.35:4443/v1/items/by/rs/?rs={rs_id}'.replace("'", "")
    response = requests.get(req_link, timeout=60)
    response = response.json()['hits']['hits']
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [types.KeyboardButton("Отправить данные"),
             types.KeyboardButton("Часто задаваемые вопросы"),
            ]
    for item in items:
        markup.add(item)
    if len(response) > 0:
        for rs in response:
            rs_for_check = rs['_source']['rs_id']
            tb.send_message(message.chat.id, f"_Мы обнаружили высокий риск развития болезни, ассоциированной с участком в геноме rs-{rs_for_check}_", parse_mode= 'Markdown')
        msg = tb.send_message(message.chat.id, "Вы можете проверить данные участки в лаборатории *Имя партнера*.\n\nПо промокоду *Deeploid* вы получите скидку в 10%", reply_markup=markup, parse_mode= 'Markdown')
    else:
        msg = tb.send_message(message.chat.id, "Мы не обнаружили никаких паталогийв вашем геноме.", reply_markup=markup, parse_mode= 'Markdown')
    tb.register_next_step_handler(msg, main_start)