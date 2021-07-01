#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, AnyStr, List, Match

from PIL import Image, ImageDraw, ImageFont, features
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from io import BytesIO
from format_timedelta import calculate_shabbat
import pyttsx3
import pytz
import random
import re
import datetime
import sys
import subprocess
import uuid
import os
import time

TOKEN = os.environ.get('BOT_TOKEN')
WHADDAYA_STOOPED = 'ну ты дурак штоле?'
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher
tz = pytz.timezone('Asia/Jerusalem')

shabaka = Image.open('./shabaka.webp')
shabaka_default_sticker = 'CAACAgIAAx0CRIwq1wACB_1e3MxXXPUDini1VgABFkMm1eMtl_MAAlYAA0lgaApie_5XONzdohoE'

shabaka_head_height = 90
shabaka_top_middle = 235
shabaka_top_width = 424
shabaka_bot_middle = 310
shabaka_bot_width = 277
default_font_size = 36
big_font = ImageFont.truetype('times-new-roman.ttf', default_font_size)

oh_pattern = re.compile(r'(\b[oо]+|\b[аa]+|\b[ы]+|\b[еe]+|\b[уy]+|\b[э]+)[xх]+\b', flags=re.IGNORECASE)
fool_pattern = re.compile(r'(\b[ё]+|\b[ю]+|\b[я]+)[xх]+\b', flags=re.IGNORECASE)
sabbath_pattern = re.compile(r'\b(шаббат\W+(?:\w+\W+)??когда|когда\W+(?:\w+\W+)??шаббат)', flags=re.IGNORECASE)
baguette_pattern = re.compile(r'(\b((хо){3,4}|багет((ь)?|(а)?|(ом)?|(ов)?|(ы)?))\b)', flags=re.IGNORECASE)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="оохххх...")


def fuck_wut(update: Update, context: CallbackContext):
    bot = context.bot
    text = update.effective_message.text
    chat_id = update.effective_chat.id

    sabbath = None
    oh = None

    fool_match = fool_pattern.search(text)
    if fool_match:
        update.effective_message.reply_text(chat_id, WHADDAYA_STOOPED, quote=True)

    oh_match = oh_pattern.search(text)
    if oh_match:
        oh = calculate_oh(oh_match)
    sabbath_match = sabbath_pattern.search(text)
    if sabbath_match:
        sabbath = calculate_shabbat(datetime.datetime.now(tz))
    baguette_match = baguette_pattern.search(text)
    has_shabaka = 'шабака' in text.lower()

    if has_shabaka:
        image = Image.new(mode='RGB', size=(shabaka.width, shabaka.height), color=(0, 0, 0))
        image.paste(shabaka, (0, 0))
        has_text = oh_match or sabbath_match or baguette_match
        if oh_match:
            image = add_text(image, oh.strip('.'), 25)
        if sabbath_match:
            image = add_text(image, sabbath, 60)
        if baguette_match:
            image = add_text(image, baguette_match.group(1), 95)
        sticker = get_image_bytes(image) if has_text else shabaka_default_sticker
        bot.send_sticker(chat_id, sticker)
    elif baguette_match:
        oh_voice = None
        sabbath_voice = None
        engine = None

        has_voice = oh_match or sabbath_match
        if has_voice:
            engine = pyttsx3.init()  # по-другому оно не работает и виснет после длинных фраз на runAndWait()
            engine.setProperty('voice', 'russian')
        if oh_match:
            oh_voice = str(uuid.uuid4()) + '.mp3'
            engine.save_to_file(oh, oh_voice)
        if sabbath_match:
            sabbath_voice = str(uuid.uuid4()) + '.mp3'
            engine.save_to_file(sabbath, sabbath_voice)
        if has_voice:
            engine.runAndWait()
            time.sleep(0.2)  # мам мультитхрединг
            del engine  # по-другому оно не работает и виснет после длинных фраз на runAndWait()

        output = run_ffmpeg(oh_voice, sabbath_voice)
        if not (os.path.exists(output)):
            return
        bot.send_video_note(chat_id, open(output, 'rb'))

        if output != './baguette.mp4':
            os.remove(output)
    elif oh_match:
        text = oh.strip('.')
        if sabbath_match:
            text += ', {}'.format(sabbath)
        bot.send_message(chat_id, text)
    elif sabbath_match:
        bot.send_message(chat_id, sabbath)


def calculate_oh(match: Optional[Match[AnyStr]]) -> str:
    return random.randint(1, 8) * match.group(1).lower()[0] + random.randint(1, 8) * 'х' + random.randint(0, 3) * '.'


def add_text(image: Image, text: str, height: int) -> Image:
    draw = ImageDraw.Draw(image)
    font = big_font
    size = draw.textsize(text, font)
    font_size = default_font_size
    if height < shabaka_head_height:
        middle = shabaka_top_middle
        box_width = shabaka_top_width
    else:
        middle = shabaka_bot_middle
        box_width = shabaka_bot_width

    while size[0] > box_width and font_size > 1:
        font_size -= 5
        if font_size < 1:
            font_size = 1
        font = ImageFont.truetype('times-new-roman.ttf', font_size)
        size = draw.textsize(text, font)
    width = middle - size[0] / 2

    draw.text((width, height), text, (255, 255, 255), font=font, align='center')
    return image


def get_image_bytes(image: Image) -> BytesIO:
    img_file = BytesIO()
    image.save(img_file, 'webp')
    img_file.seek(0)
    return img_file


def run_ffmpeg(oh_voice: str, sabbath_voice: str) -> str:
    if oh_voice is None and sabbath_voice is None:
        return './baguette.mp4'
    output = str(uuid.uuid4()) + '.mp4'
    try:
        pipe = subprocess.Popen(construct_ffmpeg_args(oh_voice, sabbath_voice, output))
        pipe.wait()
    except Exception as ex:
        print(ex)
    for voice in [oh_voice, sabbath_voice]:
        if voice is not None:
            os.remove(voice)
    return output


def construct_ffmpeg_args(oh_voice: str, sabbath_voice: str, output: str) -> List[str]:
    filter_string = '[0:a]volume=1.0[a0]; '
    args = ['ffmpeg',
            '-i', 'baguette.mp4',
            '-filter_complex',
            '-map', '0:v',
            '-map', '[out]',
            '-preset', 'ultrafast',
            output]

    inputs = 1
    if oh_voice is not None:
        filter_string += '[{0}:a]adelay=1500|1500,volume=5.0[a{0}]; '.format(inputs)
        inputs += 1
        args.insert(inputs * 2 - 1, oh_voice)
        args.insert(inputs * 2 - 1, '-i')
        filter_string += '[{0}:a]adelay=5500|5500,volume=5.0[a{0}]; '.format(inputs)
        inputs += 1
        args.insert(inputs * 2 - 1, oh_voice)
        args.insert(inputs * 2 - 1, '-i')
    if sabbath_voice is not None:
        filter_string += '[{0}:a]adelay=3200|3200,volume=5.0[a{0}]; '.format(inputs)
        inputs += 1
        args.insert(inputs * 2 - 1, sabbath_voice)
        args.insert(inputs * 2 - 1, '-i')

    for input_number in range(inputs):
        filter_string += '[a{}]'.format(input_number)
    filter_string += 'amix=inputs={}:duration=longest[out]'.format(inputs)
    args.insert(inputs * 2 + 2, filter_string)
    return args


if __name__ == '__main__':
    if not features.check_module('webp'):
        sys.exit('no webp support')
    start_handler = CommandHandler(str('start'), start)
    wut_handler = MessageHandler(Filters.text & ~Filters.update.edited_message, fuck_wut)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(wut_handler)
    updater.start_polling(drop_pending_updates=True)
    updater.idle()
