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
from telegram.constants import ChatType
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler
from telegram.ext import filters

from format_timedelta import calculate_shabbat
from response import shabaka_response, baguette_response, oh_response, neuro_response, neuro_complete

TOKEN = os.environ.get('BOT_TOKEN')
LAST_MESSAGES = 'last_messages'
application = Application.builder().token(TOKEN).build()
tz = pytz.timezone('Asia/Jerusalem')

oh_pattern = re.compile(r'(\b[oо]+|\b[аa]+|\b[ы]+|\b[еe]+|\b[уy]+|\b[э]+)[xх]+\b', flags=re.IGNORECASE)
fool_pattern = re.compile(r'(\b[ё]+|\b[ю]+|\b[я]+)[xх]+\b', flags=re.IGNORECASE)
sabbath_pattern = re.compile(r'\b(шаббат\W+(?:\w+\W+)??когда|когда\W+(?:\w+\W+)??шаббат)', flags=re.IGNORECASE)
baguette_pattern = re.compile(r'(\b((хо){3,4}|багет((ь)?|(а)?|(ом)?|(ов)?|(ы)?))\b)', flags=re.IGNORECASE)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='оохххх...')


async def huge_and_ugly_mega_text_handler_whaddaya_gonna_do_about_huh_its_my_bot(update: Update, context: CallbackContext):
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
    cleaned_from_username = cleaned_from_username.strip()
    if cleaned_from_username != '':
        last_messages.append(cleaned_from_username)

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
        await bot.send_sticker(chat_id, sticker)
    elif baguette_match:
        baguette_output = baguette_response(oh_match, sabbath_match, oh, sabbath)
        if baguette_output == '':
            return
        await bot.send_video_note(chat_id, open(baguette_output, 'rb'))
        if baguette_output != './baguette.mp4':
            os.remove(baguette_output)
    elif oh_match:
        text = oh_response(sabbath_match, oh, sabbath)
        await bot.send_message(chat_id, text)
    elif sabbath_match:
        await bot.send_message(chat_id, sabbath)
    elif update.effective_chat.type == ChatType.PRIVATE or \
            (
                    (update.effective_chat.type == ChatType.SUPERGROUP or update.effective_chat.type == ChatType.GROUP) and
                    (
                            fool_match or bot_was_mentioned or
                            (from_user == await bot.get_me() and (random.random() < 0.1 or '?' in text)) or
                            random.random() < 0.01)
            ):
        if 'допиши' in text.lower() and message.reply_to_message and message.reply_to_message.text:
            neural_text = neuro_complete(message.reply_to_message.text)
        else:
            neural_text = neuro_response(last_messages)
        last_messages.append(neural_text)
        await message.reply_text(neural_text, quote=True)


def calculate_oh(match: Optional[Match[AnyStr]]) -> str:
    return random.randint(1, 8) * match.group(1).lower()[0] + random.randint(1, 8) * 'х' + random.randint(0, 3) * '.'


if __name__ == '__main__':
    if not features.check_module('webp'):
        sys.exit('no webp support')
    start_handler = CommandHandler(str('start'), start)
    wut_handler = MessageHandler(filters.TEXT & ~filters.UpdateType.EDITED_MESSAGE,
                                 huge_and_ugly_mega_text_handler_whaddaya_gonna_do_about_huh_its_my_bot)
    application.add_handler(start_handler)
    application.add_handler(wut_handler)
    application.run_polling(drop_pending_updates=True)
