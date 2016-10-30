import time
import telepot
from telepot.namedtuple import ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from settings import *


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
        self.done = False


class Request:
    def __init__(self, chat, subject):
        self.chat = chat
        self.subject = subject


def on_chat_message(msg):
    print('msg: ', msg)
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat:', content_type, chat_type, chat_id)
    command = msg['text']

    print(' Live Users: ', live_users, '\n', 'Live Requests: ', live_requests, '\n')

    if content_type != 'text':
        return None

    if command == '/show':
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [dict(text='سایت شورا صنفی', url='http://shora.ce.sharif.edu/')],
            [InlineKeyboardButton(text='تاسیسات', callback_data='tasisat')],
            [InlineKeyboardButton(text='گمشده ها', callback_data='lost')],
            [dict(text='متن تا الان', callback_data='tillnow')],
            [dict(text='انصراف', callback_data='abort')],
        ])
        global message_with_inline_keyboard
        message_with_inline_keyboard = bot.sendMessage(chat_id, 'منو',
                                                       reply_markup=markup)
        return None

    chat = Chat(**msg['from'])
    chat_id = chat.id
    text = msg['text']

    if chat_id in live_users:
        print('Live User')
        working_request = None
        working_request_index = -1
        for req in live_requests:
            if req.chat.id == chat_id:
                working_request = req
                working_request_index = live_requests.index(working_request)
                break

        if working_request is None:
            print('working_request id None')
            working_request = Request(chat, Subject())
            live_requests.append(working_request)
            working_request_index = len(live_requests) - 1

        working_subject = working_request.subject

        if working_subject.done:
            print('working_subject is Done')
            return None

        if working_subject.item == '':
            print('If 1')
            working_subject.item = text
            working_request.subject = working_subject
            live_requests[working_request_index] = working_request
            bot.sendMessage(chat_id, 'لطفا مکان را بفرمایید', reply_markup=ForceReply())

        elif working_subject.place == '':
            print('If 2')
            working_subject.place = text
            working_request.subject = working_subject
            live_requests[working_request_index] = working_request
            bot.sendMessage(chat_id, 'توضیحات بیشتر در صورت نیاز', reply_markup=ForceReply())

        elif working_subject.more == '':
            print('If 3')
            working_subject.more = text
            working_request.subject = working_subject
            live_requests.pop(working_request_index)
            live_users.remove(chat_id)
            # commit new request
            bot.sendMessage(chat_id, 'مساله ی موردنظر شما ثبت شد' + '\n' +
                            'آیتم: ' + working_subject.item + '\n' +
                            'مکان: ' + working_subject.place + '\n' +
                            'توضیحات: ' + working_subject.more + '\n' +
                            '😜')

    else:
        print('Gazcher message')
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [dict(text='سایت شورا صنفی', url='http://shora.ce.sharif.edu/')],
            [InlineKeyboardButton(text='تاسیسات', callback_data='tasisat')],
            [InlineKeyboardButton(text='گمشده ها', callback_data='lost')],
            [dict(text='متن تا الان', callback_data='tillnow')],
            [dict(text='انصراف', callback_data='abort')],
        ])
        global message_with_inline_keyboard
        message_with_inline_keyboard = bot.sendMessage(chat_id, 'منو',
                                                       reply_markup=markup)


def on_edited_chat_message(msg):
    print('Edit kard')
    content_type, chat_type, chat_id = telepot.glance(msg, flavor='edited_chat')
    bot.sendMessage(chat_id, 'ادیت نکن دیگه🙈', reply_to_message_id=msg['message_id'])


def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print('Callback query:', query_id, from_id, data)

    if data == 'tasisat':
        print('Tasisat callback')
        live_users.append(from_id)
        bot.sendMessage(from_id, 'لطفا آیتم مورد نظر را بفرمایید', reply_markup=ForceReply())
    elif data == 'lost':
        print('lost callback')
        live_users.append(from_id)
        bot.sendMessage(from_id, 'لطفا آیتم مورد نظر را بفرمایید', reply_markup=ForceReply())
    elif data == 'tillnow':
        print('tillnow callback')
        if from_id not in live_users:
            bot.answerCallbackQuery(query_id, text='هنوز چیزی نگفتی که!', show_alert=True)
            return None
        for req in live_requests:
            if req.chat.id == from_id:
                bot.answerCallbackQuery(query_id, 'متن تا الان: ' + '\n' +
                                        'آیتم: ' + req.subject.item + '\n' +
                                        'مکان: ' + req.subject.place + '\n' +
                                        'توضیحات: ' + req.subject.more + '\n' +
                                        '😜', show_alert=True)
                break
    elif data == 'abort':
        print('abort callback')
        if from_id not in live_users:
            print('If 1 callback')
            bot.answerCallbackQuery(query_id, text='هنوز چیزی نگفتی که!', show_alert=True)
            return None
        if from_id in live_users:
            print('If 2 callback')
            live_users.remove(from_id)
        for req in live_requests:
            if req.chat.id == from_id:
                print('If 3 callback')
                live_requests.remove(req)
                break
        bot.answerCallbackQuery(query_id, text='حلله!', show_alert=True)


bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

bot.message_loop({'chat': on_chat_message,
                  'edited_chat': on_edited_chat_message,
                  'callback_query': on_callback_query})
print('Listening ...')

while 1:
    time.sleep(SLEEP_TIME)
