import asyncio
import os
from PIL import Image, ImageDraw
import telebot
import telebot.async_telebot
import telebot.types as t
from telebot.formatting import escape_html
from data import TOKEN, OWNER_ID, OWNER_HANDLE, BOT_HANDLE, MAX_LINE_LEN, BASE_FONT, IMAGE_CHAT
import utils as u

ImageDraw.ImageDraw.font = BASE_FONT

class MyExceptionHandler(telebot.ExceptionHandler):
    async def handle(self, exc: Exception):
        message = None
        inline_query = None
        reply_markup = None
        tb = exc.__traceback__
        while (tb := tb.tb_next):
            # print(tb.tb_frame)
            if 'message' in tb.tb_frame.f_locals:
                message = tb.tb_frame.f_locals['message']
                if isinstance(message, t.Message):
                    break
                message = None
            if 'inline_query' in tb.tb_frame.f_locals:
                inline_query = tb.tb_frame.f_locals['inline_query']
                if isinstance(inline_query, t.InlineQuery):
                    break
                inline_query = None
        if not (message or inline_query):
            return False
        contact_note = ((message or inline_query).from_user.id != OWNER_ID)
        handled = False
        if isinstance(exc, u.UserError):
            error_message = "⚠️ Ошибка!\n" + str(exc)
            handled = True
            reply_markup = exc.reply_markup
            contact_note = contact_note and exc.contact_note
        else:
            traceback = exc.__traceback__
            while traceback.tb_next: traceback = traceback.tb_next
            filename = os.path.split(traceback.tb_frame.f_code.co_filename)[1]
            line_number = traceback.tb_lineno
            error_message = (f"⚠️ Во время выполнения операции произошла ошибка:\n"
                             f"<code>{exc.__class__.__name__} "
                             f"({filename}, строка {line_number}): {' '.join([escape_html(str(arg)) for arg in exc.args])}</code>")
        if contact_note:
            error_message += f"\nЕсли тебе кажется, что это баг, сообщи {OWNER_HANDLE}"
        if message:
            await bot.send_message(message.chat.id, error_message, reply_markup=reply_markup)
        else:
            await bot.answer_inline_query(
                inline_query.id, [t.InlineQueryResultArticle(
                    "0", "Ошибка",
                    t.InputTextMessageContent(error_message, parse_mode="HTML"),
                    description=error_message
                )]
            )
        return handled

bot = telebot.async_telebot.AsyncTeleBot(
    TOKEN,
    parse_mode="HTML",
    # use_class_middlewares=True,
    disable_web_page_preview=True,
    exception_handler=MyExceptionHandler()
)

@bot.message_handler(func=lambda _: True, content_types=['text', 'audio', 'photo', 'voice', 'video', 'document'])
async def handle_message(message: t.Message):
    response = (
        f"Пока что я умею работать только в inline-режиме.\n"
        f"Напиши {BOT_HANDLE} в начале сообщения в любом чате, "
        f"чтобы отправить сообщение на шрифте РЖЯ!"
    )
    if message.from_user.id == OWNER_ID:
        response += f"\nЧат: <code>{message.chat.id}</code>"
    await bot.send_message(message.chat.id, response)

@bot.inline_handler(func=lambda _: True)
async def handle_query(inline_query: t.InlineQuery):
    text = inline_query.query
    if not text:
        return
    wrapped = u.get_wrapped_text(text, BASE_FONT, MAX_LINE_LEN)
    dummy_image = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_image)
    _, _, w, h = dummy_draw.multiline_textbbox((0, 0), wrapped, BASE_FONT)
    margins = 5
    image = Image.new("RGBA", (w+2*margins, h+2*margins))
    draw = ImageDraw.Draw(image)
    u.draw_text(draw, wrapped, BASE_FONT, MAX_LINE_LEN, margins, already_wrapped=True)
    file_id = await u.save_temporarily(image, bot, IMAGE_CHAT)
    result = t.InlineQueryResultPhoto("1", file_id, file_id, caption=f"<code>{escape_html(text)}</code>", parse_mode="HTML")
    await bot.answer_inline_query(inline_query.id, [result], cache_time=0)

print("Запускаю бота...")
asyncio.run(bot.polling())