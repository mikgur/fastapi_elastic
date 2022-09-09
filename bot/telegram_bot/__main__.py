import telebot
from telebot import types
import os
import requests
import time
from . import headlines
import numpy as np

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
        path = os.path.join(os.path.dirname(__file__), 'load/data',f'{message.chat.id}_{ts}.txt')  
        src = path + message.document.file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        msg = tb.reply_to(message, "*Спасибо!*\n\n*Мой искусственный интелект начал обрабатывать информацию!*\n\n⚙️⚙️⚙️⚙️⚙️⚙️⚙️⚙️\n\n_Как только я закончу, я пришлю информацию моего анализа._", parse_mode= 'Markdown')
        process(message=msg, file_name=src)
    except Exception as e:
        msg = tb.reply_to(message, '*Упс!*\n\nКажется в вашем файле проблемы! Проверьте точно ли вы загружаете нужный файл!\n\n_По любым вопросам можно обратиться к моим разработчикам_\n@voronik1801', parse_mode= 'Markdown')
        tb.register_next_step_handler(msg, handle_docs_photo)

def process(message, file_name):
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