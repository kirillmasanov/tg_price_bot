import logging

from pymongo import MongoClient
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from datetime import date

from settings import *
from data import main_data

db = MongoClient(MONGO_LINK)[MONGO_DB]


def get_keyboard():
    my_keyboard = ReplyKeyboardMarkup([
        ['1Tb', '2Tb'],
        ['Прислать данные']
    ], resize_keyboard=True)
    return my_keyboard


def greet_user(update: Update, context: CallbackContext):
    text = 'Привет!'
    logging.info(text)
    update.message.reply_text(text, reply_markup=get_keyboard())


def get_create_data(context: CallbackContext):
    for item in main_data():
        position = db.items.find_one({'article': item['article']})
        if not position:
            position = {'article': item['article'],
                        'name': item['name'],
                        'price': item['price'],
                        'date': str(date.today())
                        }
            db.items.insert_one(position)
            text_1 = f"new! {item['name']} - {item['price']} руб."
            context.bot.send_message(chat_id=my_chat_id, text=text_1)
        else:
            new_price = item['price']
            if position['price'] == new_price:
                print('Такая есть!')
            else:
                print(f'Новая цена: {new_price}')
                db.items.update_one(
                    {'article': item['article']},
                    {'$set': {'price': item['price'],
                              'date': str(date.today())}}
                )
                dif_price = position['price'] - item['price']
                text_2 = f"Изменилась цена на {item['name']} - было {position['price']}, стало {item['price']} ({dif_price} руб.)"
                context.bot.send_message(chat_id=my_chat_id, text=text_2)


def send_data(update: Update, context: CallbackContext):
    for item in main_data():
        text = f"{item['name']} - {item['price']} руб."
        update.message.reply_text(text, reply_markup=get_keyboard())


def send_1tb(update: Update, context: CallbackContext):
    key = True
    for item in main_data():
        if '1Tb' in item['name']:
            key = False
            text = f"{item['name']} - {item['price']} руб."
            update.message.reply_text(text, reply_markup=get_keyboard())
    if key:
        update.message.reply_text('1Tb макбуков нет в наличии!', reply_markup=get_keyboard())


def send_2tb(update: Update, context: CallbackContext):
    key = True
    for item in main_data():
        if '2Tb' in item['name']:
            key = False
            text = f"{item['name']} - {item['price']} руб."
            update.message.reply_text(text, reply_markup=get_keyboard())
    if key:
        update.message.reply_text('2Tb макбуков нет в наличии!', reply_markup=get_keyboard())


def talk_to_me(update: Update, context: CallbackContext):
    print(context.user_data)
    user_text = f'Привет, {update.message.chat.first_name}! Ты написал: {update.message.text}'
    logging.info(f'User: {update.message.chat.username}, Chat_id: {update.message.chat_id}, '
                 f'Message: {update.message.text}')
    update.message.reply_text(user_text, reply_markup=get_keyboard())
