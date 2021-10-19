import os
import time
import uuid
from typing import List

import pyttsx3
from PIL import Image
from transformers import GPT2LMHeadModel, GPT2Tokenizer

from draw import shabaka, add_text, get_image_bytes, shabaka_default_sticker
from ffmpeg import run_ffmpeg


def shabaka_response(oh_match, sabbath_match, baguette_match, oh, sabbath):
    image = Image.new(mode='RGB', size=(shabaka.width, shabaka.height), color=(0, 0, 0))
    image.paste(shabaka, (0, 0))
    has_text = oh_match or sabbath_match or baguette_match
    if oh_match:
        image = add_text(image, oh.strip('.'), 25)
    if sabbath_match:
        image = add_text(image, sabbath, 60)
    if baguette_match:
        image = add_text(image, baguette_match.group(1), 95)
    return get_image_bytes(image) if has_text else shabaka_default_sticker


def baguette_response(oh_match, sabbath_match, oh, sabbath) -> str:
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
        return ''
    return output


def oh_response(sabbath_match, oh, sabbath) -> str:
    text = oh.strip('.')
    if sabbath_match:
        text += ', {}'.format(sabbath)
    return text


def neuro_response(last_messages: List[str]) -> str:
    prompt = '\n'.join(last_messages) + '\n'
    tok = GPT2Tokenizer.from_pretrained('models/')
    model = GPT2LMHeadModel.from_pretrained('models/')
    model.cpu()
    inpt = tok.encode(prompt, return_tensors='pt')
    out = model.generate(inpt.cpu(), max_length=150, repetition_penalty=5.0, do_sample=True, top_k=5, top_p=0.95,
                         temperature=0.8)
    generated = tok.decode(out[0])
    print(generated)  # sorta debug
    cleaned = generated[len(prompt):]
    happy = cleaned.find('))')
    sad = cleaned.find('((')
    if happy != -1 and sad != -1:
        smiley_index = min(happy, sad)
    else:
        smiley_index = max(happy, sad)
    if smiley_index != -1:
        if len(cleaned) - smiley_index > 5:
            smiley_index += 3
        cleaned = cleaned[:smiley_index]
    single_quote = cleaned.count('"')
    if single_quote % 2 != 0:
        single_quote_index = cleaned.rfind('"')
        if single_quote_index > 0:
            cleaned = cleaned[:single_quote_index]
    return cleaned
