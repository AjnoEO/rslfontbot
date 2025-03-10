import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InputFile

default_bot = None
default_chat = None

class UserError(Exception):
    """Ошибки, вызванные неправильными действиями пользователей"""
    def __init__(self, *args, contact_note = True, reply_markup = None):
        super().__init__(*args)
        self.reply_markup = reply_markup
        self.contact_note = contact_note

async def save_temporarily(
        images: Image.Image | list[Image.Image] | None,
        bot: AsyncTeleBot, image_chat: int
    ) -> str | list[str] | None:
    """Сохранить изображения в чате и вернуть соответствующие file_id"""
    if images is None:
        return None
    temp_path = "temp"
    Path(temp_path).mkdir(parents=True, exist_ok=True)
    arg_is_list = isinstance(images, list)
    if arg_is_list:
        imlist = []
    else:
        images = [images]
    for im in images:
        while True:
            filename = "".join(chr(random.randint(ord("a"), ord("z"))) for _ in range(8))
            path = os.path.join(temp_path, filename + ".png")
            if path not in os.listdir(temp_path): break
        im.save(path)
        msg = await bot.send_photo(image_chat, InputFile(path))
        os.remove(path)
        file_id = msg.photo[0].file_id
        if not arg_is_list:
            return file_id
        imlist.append(file_id)
    return imlist

def get_wrapped_text(text: str | list[str], font: ImageFont.ImageFont,
                     line_length: int):
    lines = ['']
    if isinstance(text, str):
        text = text.replace('\n', ' \n ')
        text = text.split(' ')
    while text:
        word = text.pop(0)
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        elif lines[-1]:
            lines.append('')
            text = [word] + text
        else:
            line = ''
            while font.getlength(line + word[0]) <= line_length:
                line += word[0]
                word = word[1:]
            lines[-1] = line
            text = [word] + text
    if not lines[0] or lines[0].isspace():
        lines.pop(0)
    return '\n'.join(lines)

def draw_text(draw: ImageDraw.ImageDraw, text: str | list[str],
              font: ImageFont.ImageFont, line_length: int,
              margin: int, already_wrapped: bool = False):
    if not already_wrapped:
        text = get_wrapped_text(text, font, line_length)
    offset = margin
    draw.multiline_text((margin, offset), text, font=font, fill="#000000FF")
