from io import BytesIO
import os
from configparser import ConfigParser
from PIL import ImageFont
import requests

if os.path.exists("config.ini"):
    __config = ConfigParser()
    __config.read("config.ini")
else:
    raise FileExistsError("Отсутствует файл config.ini.\n"
                          "Если вы клонировали или запуллили git-репозиторий, "
                          "убедитесь, что вы скопировали example.config.ini, "
                          "переименовали его config.ini и исправили под себя.")

__data = __config["data"]
TOKEN = __data["token"]
OWNER_ID = int(__data["owner_id"])
OWNER_HANDLE = __data["owner_handle"]
BOT_HANDLE = __data["bot_handle"]
IMAGE_CHAT = int(__data["image_chat"])

__font_source = "https://ajnoeo.github.io/rslfont/RSL_font/symbol_font_for_rsl/rsl-font.ttf"
__response = requests.get(__font_source)

FONT_SIZE = 36
MAX_LINE_LEN = 700
BASE_FONT = ImageFont.truetype(font=BytesIO(__response.content), size=36)
