from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode, error, InlineKeyboardButton, \
    InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

import logging

from db import db, get_create_data
from data import *


def get_keyboard():
    my_keyboard = ReplyKeyboardMarkup([
        ['Прислать данные']
    ], resize_keyboard=True)
    return my_keyboard

def greet_user(update: Update, context: CallbackContext):
    text = 'Привет!'
    logging.info(text)
    update.message.reply_text(text, reply_markup=get_keyboard())


def send_data(update: Update, context: CallbackContext):
    text = get_create_data()
    update.message.reply_text(text, reply_markup=get_keyboard())





def send_pic(update: Update, context: CallbackContext):
    user = get_or_create_user(db, update.effective_user, update.message)
    inlinekbd = [[InlineKeyboardButton(emojize(':thumbs_up:'), callback_data='cat_good'),
                  InlineKeyboardButton(emojize(':thumbs_down:'), callback_data='cat_bad')]]
    kbd_murkup = InlineKeyboardMarkup(inlinekbd)
    context.bot.send_photo(chat_id=update.message.chat_id,
                           photo='https://i.pinimg.com/736x/c7/12/43/c712434d2bf453f77513c0de26d3b4d1.jpg',
                           reply_markup=kbd_murkup
                           )


def talk_to_me(update: Update, context: CallbackContext):
    print(context.user_data)
    emo = get_user_emo(context.user_data)
    user_text = f'Привет, {update.message.chat.first_name}! Ты написал: {update.message.text}{emo}'
    logging.info(f'User: {update.message.chat.username}, Chat_id: {update.message.chat_id}, '
                 f'Message: {update.message.text}')
    update.message.reply_text(user_text, reply_markup=get_keyboard())


def get_contact(update: Update, context: CallbackContext):
    print(update.message.contact)
    update.message.reply_text(f'Готово: {get_user_emo(context.user_data)}', reply_markup=get_keyboard())


def get_location(update: Update, context: CallbackContext):
    print(update.message.location)
    update.message.reply_text(f'Готово: {get_user_emo(context.user_data)}', reply_markup=get_keyboard())


def change_user_emo(update: Update, context: CallbackContext):
    if 'emo' in context.user_data:
        del context.user_data['emo']
    emo = get_user_emo(context.user_data)
    update.message.reply_text(f'У вас новый смайлик - {emo}', reply_markup=get_keyboard())


def describe_photo(update: Update, context: CallbackContext):
    update.message.reply_text(f'Обрабатываем фото..')
    photo_file = context.bot.getFile(update.message.photo[-1].file_id)
    photo_path = photo_file['file_path']
    update.message.reply_text(f'Ключевые слова: {", ".join(pic_info(photo_path))}')


def anketa_start(update: Update, context: CallbackContext):
    update.message.reply_text(f'Как Вас зовут? Напишите имя и фамилию', reply_markup=ReplyKeyboardRemove())
    return 'name'


def anketa_get_name(update: Update, context: CallbackContext):
    user_name = update.message.text
    if len(user_name.split(' ')) != 2:
        update.message.reply_text('Ошибка! Попробуйте еще раз!')
        return 'name'
    else:
        context.user_data['anketa_name'] = user_name
        reply_keyboard = [['1', '2', '3', '4', '5']]

        update.message.reply_text(
            'Оцените нашего бота от 1 до 5',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return 'rating'


def anketa_rating(update: Update, context: CallbackContext):
    context.user_data['anketa_rating'] = update.message.text
    update.message.reply_text('''Пожалуйста, напишите нам отзыв в свободной форме 
или /skip, чтобы пропустить этот шаг''')
    return 'comment'


def anketa_comment(update: Update, context: CallbackContext):
    context.user_data['anketa_comment'] = update.message.text
    text = """
<b>Фамилия Имя:</b> {anketa_name}
<b>Оценка:</b> {anketa_rating}
<b>Комментарий:</b> {anketa_comment}""".format(**context.user_data)
    update.message.reply_text(text, reply_murkup=get_keyboard(), parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def anketa_skip_comment(update: Update, context: CallbackContext):
    text = """
<b>Фамилия Имя:</b> {anketa_name}
<b>Оценка:</b> {anketa_rating}""".format(**context.user_data)
    update.message.reply_text(text, reply_murkup=get_keyboard(), parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def dontknow(update: Update, context: CallbackContext):
    update.message.reply_text('Не понимаю!')


def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def userinfo(update, context):
    user_name = update.message.chat.username
    chat_id = update.message.chat.id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    # print(f'{update.message}')
    update.message.reply_text(f'@{user_name}\nid: {chat_id}\nFirst: {first_name}\nLast: {last_name}')


def set_alarm(update, context):
    try:
        seconds = int(context.args[0])
        context.job_queue.run_once(alarm, seconds, context=update.message.chat_id)
    except (IndexError, ValueError):
        update.message.reply_text('Введите кол-во секунд после /alarm')
    update.message.reply_text('Timer successfully set!')


def alarm(context):
    job = context.job
    context.bot.send_message(job.context, text='Сработал будильник!')


def subscribe(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    if not user.get('subscribed'):
        toggle_subscription(db, user)
    update.message.reply_text('Вы подписались!')


def send_updates(context):
    for user in get_subscribers(db):
        try:
            context.bot.sendMessage(chat_id=user['chat_id'], text='BUZZZ!')
        except error.BadRequest:
            print(f'Chat {user["chat_id"]} not found!')


def unsubscribe(update, context):
    user = get_or_create_user(db, update.effective_user, update.message)
    if user.get('subscribed'):
        toggle_subscription(db, user)
        update.message.reply_text('Вы отписались!')
    else:
        update.message.reply_text('Вы не подписаны, нажмите /subscribe , чтобы подписаться!')


def inline_button_pressed(update, context, *args, **kwargs):
    query = update.callback_query
    if query.data in ['cat_good', 'cat_bad']:
        caption = 'Круто!' if query.data == 'cat_good' else 'Печаль :('
        context.bot.edit_message_caption(caption=caption,
                                         chat_id=update.callback_query.message.chat_id,
                                         message_id=update.callback_query.message.message_id,
                                         *args, **kwargs)
