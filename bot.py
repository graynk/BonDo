#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import datetime
import os
import random
import re
import sys
from typing import Optional, AnyStr, Match

import pytz
from PIL import features
from telegram import Update
from telegram.constants import CHAT_SUPERGROUP, CHAT_GROUP, CHAT_PRIVATE
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from format_timedelta import calculate_shabbat
from response import shabaka_response, baguette_response, oh_response, neuro_response

TOKEN = os.environ.get('BOT_TOKEN')
LAST_MESSAGES = 'last_messages'
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher
tz = pytz.timezone('Asia/Jerusalem')

oh_pattern = re.compile(r'(\b[oо]+|\b[аa]+|\b[ы]+|\b[еe]+|\b[уy]+|\b[э]+)[xх]+\b', flags=re.IGNORECASE)
fool_pattern = re.compile(r'(\b[ё]+|\b[ю]+|\b[я]+)[xх]+\b', flags=re.IGNORECASE)
sabbath_pattern = re.compile(r'\b(шаббат\W+(?:\w+\W+)??когда|когда\W+(?:\w+\W+)??шаббат)', flags=re.IGNORECASE)
baguette_pattern = re.compile(r'(\b((хо){3,4}|багет((ь)?|(а)?|(ом)?|(ов)?|(ы)?))\b)', flags=re.IGNORECASE)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='оохххх...')


def huge_and_ugly_mega_text_handler_whaddaya_gonna_do_about_huh_its_my_bot(update: Update, context: CallbackContext):
    bot = context.bot
    bot_username = '@{}'.format(bot.username)
    message = update.effective_message
    text = message.text
    chat_id = update.effective_chat.id
    if LAST_MESSAGES not in context.chat_data:
        context.chat_data[LAST_MESSAGES] = collections.deque([], 5)
    last_messages = context.chat_data[LAST_MESSAGES]
    cleaned_from_username = text.replace(bot_username, '')
    bot_was_mentioned = len(text) != len(cleaned_from_username)
    last_messages.append(cleaned_from_username.strip())

    sabbath = None
    oh = None
    from_user = message.reply_to_message.from_user if message.reply_to_message else None

    fool_match = fool_pattern.search(text)
    oh_match = oh_pattern.search(text)
    if oh_match:
        oh = calculate_oh(oh_match)
    sabbath_match = sabbath_pattern.search(text)
    if sabbath_match:
        sabbath = calculate_shabbat(datetime.datetime.now(tz))
    baguette_match = baguette_pattern.search(text)
    has_shabaka = 'шабака' in text.lower()

    if has_shabaka:
        sticker = shabaka_response(oh_match, sabbath_match, baguette_match, oh, sabbath)
        bot.send_sticker(chat_id, sticker)
    elif baguette_match:
        baguette_output = baguette_response(oh_match, sabbath_match, oh, sabbath)
        if baguette_output == '':
            return
        bot.send_video_note(chat_id, open(baguette_output, 'rb'))
        if baguette_output != './baguette.mp4':
            os.remove(baguette_output)
    elif oh_match:
        text = oh_response(sabbath_match, oh, sabbath)
        bot.send_message(chat_id, text)
    elif sabbath_match:
        bot.send_message(chat_id, sabbath)
    elif update.effective_chat.type == CHAT_PRIVATE or \
            (
                    (update.effective_chat.type == CHAT_SUPERGROUP or update.effective_chat.type == CHAT_GROUP) and
                    (fool_match or bot_was_mentioned or from_user == bot.get_me() or random.random() < 0.01)
            ):
        neural_text = neuro_response(last_messages)
        message.reply_text(neural_text, quote=True)


def calculate_oh(match: Optional[Match[AnyStr]]) -> str:
    return random.randint(1, 8) * match.group(1).lower()[0] + random.randint(1, 8) * 'х' + random.randint(0, 3) * '.'


if __name__ == '__main__':
    if not features.check_module('webp'):
        sys.exit('no webp support')
    start_handler = CommandHandler(str('start'), start)
    wut_handler = MessageHandler(Filters.text & ~Filters.update.edited_message,
                                 huge_and_ugly_mega_text_handler_whaddaya_gonna_do_about_huh_its_my_bot)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(wut_handler)
    updater.start_polling(drop_pending_updates=True)
    updater.idle()
