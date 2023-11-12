from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

shabaka = Image.open('./shabaka.webp')
shabaka_default_sticker = 'CAACAgIAAx0CRIwq1wACB_1e3MxXXPUDini1VgABFkMm1eMtl_MAAlYAA0lgaApie_5XONzdohoE'

shabaka_head_height = 90
shabaka_top_middle = 235
shabaka_top_width = 424
shabaka_bot_middle = 310
shabaka_bot_width = 277
default_font_size = 36
big_font = ImageFont.truetype('times-new-roman.ttf', default_font_size)


def add_text(image: Image, text: str, height: int) -> Image:
    draw = ImageDraw.Draw(image)
    font = big_font
    size = draw.textbbox((0, 0), text, font=font)
    font_size = default_font_size
    if height < shabaka_head_height:
        middle = shabaka_top_middle
        box_width = shabaka_top_width
    else:
        middle = shabaka_bot_middle
        box_width = shabaka_bot_width

    while size[2] > box_width and font_size > 1:
        font_size -= 5
        if font_size < 1:
            font_size = 1
        font = ImageFont.truetype('times-new-roman.ttf', font_size)
        size = draw.textbbox((0, 0), text, font)
    width = middle - size[2] / 2

    draw.text((width, height), text, (255, 255, 255), font=font, align='center')
    return image


def get_image_bytes(image: Image) -> BytesIO:
    img_file = BytesIO()
    image.save(img_file, 'webp')
    img_file.seek(0)
    return img_file
