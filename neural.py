import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('starting on {}'.format(device))
tok = GPT2Tokenizer.from_pretrained('models/')
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
model = GPT2LMHeadModel.from_pretrained('models/')
model.to(device)
MAX_LENGTH = 150


def clean(generated: str) -> str:
    cleaned = generated
    happy = cleaned.find('))')
    sad = cleaned.find('((')
    if happy != -1 and sad != -1:
        smiley_index = min(happy, sad)
    else:
        smiley_index = max(happy, sad)
    if smiley_index != -1:
        smiley_index += 3
        cleaned = cleaned[:smiley_index]
    single_quote = cleaned.count('"')
    if single_quote % 2 != 0:
        single_quote_index = cleaned.rfind('"')
        if single_quote_index > 0:
            cleaned = cleaned[:single_quote_index]
    return cleaned


def generate_and_clean(prompt: str) -> str:
    inpt = tok.encode(prompt, return_tensors='pt')
    out = model.generate(inpt.to(device),
                         max_length=MAX_LENGTH + (len(prompt) / 3),
                         repetition_penalty=5.0,
                         do_sample=True,
                         top_k=5,
                         top_p=0.95,
                         temperature=0.8,
                         pad_token_id=tok.pad_token_id)
    generated = tok.decode(out[0])
    print(generated)  # sorta debug
    generated = generated[len(prompt):]
    cleaned = clean(generated)
    end = cleaned.find('.', MAX_LENGTH)
    if end == -1:
        end = cleaned.find('?', MAX_LENGTH)
    if end == -1:
        end = cleaned.find('!', MAX_LENGTH)
    if end == -1:
        end = MAX_LENGTH
    return cleaned[:end]
