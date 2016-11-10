import time
import telepot
from telepot.namedtuple import ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from settings import *
from shora_api import *

message_with_inline_keyboard = None
live_users = []
live_requests = []


class Chat:
    def __init__(self, id, username=None, first_name=None, last_name=None):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name


class Subject:
    def __init__(self):
        self.item = ''
        self.place = ''
        self.more = ''
        self.type = 0  # 1 ----> tasisat, 2 ----> lost


class Request:
    def __init__(self, chat, subject):
        self.chat = chat
        self.subject = subject


def on_chat_message(msg):
    # print('msg: ', msg)
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type != 'text':
        bot.sendMessage(chat_id, 'آر یو کیدینگ می؟')
        return None
    # print('Chat:', content_type, chat_type, chat_id)
    command = msg['text']

    # print(' Live Users: ', live_users, '\n', 'Live Requests: ', live_requests, '\n')

    if content_type != 'text':
        return None

    if command == '/show':
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [dict(text='سایت شورا صنفی', url='http://shora.ce.sharif.edu/')],
            [InlineKeyboardButton(text='تاسیسات', callback_data='tasisat')],
            [InlineKeyboardButton(text='گمشده ها', callback_data='lost')],
        ])
        global message_with_inline_keyboard
        message_with_inline_keyboard = bot.sendMessage(chat_id, 'منو',
                                                       reply_markup=markup)
        return None

    if command == '/done':
        working_request = None
        working_request_index = -1
        for req in live_requests:
            if req.chat.id == chat_id:
                working_request = req
                working_request_index = live_requests.index(working_request)
                break
        if working_request_index == -1:
            bot.sendMessage(chat_id, 'چیزی نگفتی که هنوز 🤔')
            return None
        if working_request.subject.item == '' or working_request.subject.place == '':
            bot.sendMessage(chat_id, 'مورد یا مکان رو هنوز مشخص نکردی 😁')
            return None
        shora_api.send_message(ShoraMessage(working_request.subject.item,
                                            working_request.subject.place,
                                            working_request.subject.more))
        # commit new request
        live_requests.pop(working_request_index)
        live_users.remove(chat_id)
        bot.sendMessage(chat_id, 'مساله ی موردنظر شما ثبت شد' + '\n' +
                        'آیتم: ' + working_request.subject.item + '\n' +
                        'مکان: ' + working_request.subject.place + '\n' +
                        'توضیحات: ' + working_request.subject.more + '\n' +
                        '😜')
        if working_request.subject.type == 1:
            bot.sendMessage(chat_id,
                            'ما پیگیر مساله ثبت شده شما هستیم و آن را در لیست کارهای بخش تاسیسات قرار خواهیم داد.')
        elif working_request.subject.type == 2:
            bot.sendMessage(chat_id, 'امیدواریم وسیله گم شده ی خود را هر چه زودتر پیدا کنید.')
        return None

    if command == '/cancel':
        if chat_id not in live_users:
            bot.sendMessage(chat_id, 'هنوز چیزی نگفتی 🤔')
            return None
        if chat_id in live_users:
            live_users.remove(chat_id)
        for req in live_requests:
            if req.chat.id == chat_id:
                live_requests.remove(req)
                bot.sendMessage(chat_id, 'حلله ✋🏻')
                break
        return None

    if command == '/content':
        # print('content')
        if chat_id not in live_users:
            bot.sendMessage(chat_id, 'هنوز چیزی نگفتی 🤔')
            return None
        for req in live_requests:
            if req.chat.id == chat_id:
                bot.sendMessage(chat_id, 'متن تا الان: ' + '\n' +
                                'آیتم: ' + req.subject.item + '\n' +
                                'مکان: ' + req.subject.place + '\n' +
                                'توضیحات: ' + req.subject.more + '\n' +
                                '😜')
        return None

    chat = Chat(**msg['from'])
    chat_id = chat.id
    text = msg['text']

    if chat_id in live_users:
        # print('Live User')
        working_request = None
        working_request_index = -1
        for req in live_requests:
            if req.chat.id == chat_id:
                working_request = req
                working_request_index = live_requests.index(working_request)
                break

        if working_request is None:
            # print('working_request id None')
            working_request = Request(chat, Subject())
            live_requests.append(working_request)
            working_request_index = len(live_requests) - 1

        working_subject = working_request.subject

        # a little hard coded, i know
        if 'reply_to_message' in msg:
            if 'گزارش' in msg['reply_to_message']['text']:
                working_subject.type = 1
            elif 'گم' in msg['reply_to_message']['text']:
                working_subject.type = 2

        if working_subject.item == '':
            # print('If 1')
            working_subject.item = text
            working_request.subject = working_subject
            live_requests[working_request_index] = working_request
            bot.sendMessage(chat_id, 'لطفا محل موردنظر را بفرمایید', reply_markup=ForceReply())

        elif working_subject.place == '':
            # print('If 2')
            working_subject.place = text
            working_request.subject = working_subject
            live_requests[working_request_index] = working_request
            bot.sendMessage(chat_id, 'توضیحات بیشتر (اگر نیاز به توضیح ندارد /done را بزنید)',
                            reply_markup=ForceReply())

        elif working_subject.more == '':
            # print('If 3')
            working_subject.more = text
            working_request.subject = working_subject
            live_requests.pop(working_request_index)
            live_users.remove(chat_id)

            shora_api.send_message(ShoraMessage(working_subject.item,
                                                working_subject.place,
                                                working_subject.more))
            # commit new request
            bot.sendMessage(chat_id, 'مساله ی موردنظر شما ثبت شد' + '\n' +
                            'آیتم: ' + working_subject.item + '\n' +
                            'مکان: ' + working_subject.place + '\n' +
                            'توضیحات: ' + working_subject.more + '\n' +
                            '😜')
            if working_subject.type == 1:
                bot.sendMessage(chat_id,
                                'ما پیگیر مساله ثبت شده شما هستیم و آن را در لیست کارهای بخش تاسیسات قرار خواهیم داد.')
            elif working_subject.type == 2:
                bot.sendMessage(chat_id, 'امیدواریم وسیله گم شده ی خود را هر چه زودتر پیدا کنید.')

    else:
        # print('Gazcher message')
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [dict(text='سایت شورا صنفی', url='http://shora.ce.sharif.edu/')],
            [InlineKeyboardButton(text='تاسیسات', callback_data='tasisat')],
            [InlineKeyboardButton(text='گمشده ها', callback_data='lost')],
        ])
        global message_with_inline_keyboard
        message_with_inline_keyboard = bot.sendMessage(chat_id, 'منو',
                                                       reply_markup=markup)


def on_edited_chat_message(msg):
    # print('Edit kard')
    content_type, chat_type, chat_id = telepot.glance(msg, flavor='edited_chat')
    bot.sendMessage(chat_id, 'ادیت نکن دیگه🙈', reply_to_message_id=msg['message_id'])


def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    # print('Callback query:', query_id, from_id, data)

    if data == 'tasisat':
        # print('Tasisat callback')
        if from_id in live_users:
            bot.sendMessage(from_id, 'یدونه یدونه!')
            return None
        live_users.append(from_id)
        bot.sendMessage(from_id, 'لطفا عنوان گزارش یا پیشنهاد خود را بفرمایید', reply_markup=ForceReply())
    elif data == 'lost':
        # print('lost callback')
        if from_id in live_users:
            bot.sendMessage(from_id, 'یدونه یدونه!')
            return None
        live_users.append(from_id)
        bot.sendMessage(from_id, 'لطفا عنوان وسیله پیداشده یا گم شده را بفرمایید', reply_markup=ForceReply())


# almost one to go
shora_api = ShoraAPI(SHORA_CALLBACK_URL, SIGNING_SECRET)
bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

bot.message_loop({'chat': on_chat_message,
                  'edited_chat': on_edited_chat_message,
                  'callback_query': on_callback_query})
print('Listening ...')

while 1:
    time.sleep(SLEEP_TIME)
