from io import BytesIO
from textwrap import wrap
from asyncio import sleep
from aiogram.types import Message
from .config import CHAR_LIMIT


class DocumentManager:

    """
    Контекстный менеджер для скачивания файлов aiogram3 и их обработки в теле менеджера.
    """

    def __init__(self, message: Message):
        self.message = message
        self.bytes_io = None
        self.file = None

    async def __aenter__(self):
        self.bytes_io = BytesIO()
        bot = self.message.bot
        doc = self.message.document
        file_id = doc.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        self.file = await bot.download_file(file_path, self.bytes_io)
        return self.bytes_io

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        self.bytes_io.close()


async def split_and_send(message: Message, text: str, char_limit: int = CHAR_LIMIT):

    """
    Функция отправляет сообщение, если оно не превышает лимит char_limit.
    В ином случае разбивает длинный текст на части <= char_limit символов
    и с задержкой в 0.33 сек. отправляет пользователю.

    :param message: объект сообщения пользователя.
    :param text: текст для отправки.
    :param char_limit: лимит символов на одно сообщение.
    :return:
    """

    if len(text) > CHAR_LIMIT:
        for text_chunk in wrap(text=text, width=char_limit, replace_whitespace=False):
            await sleep(0.33)
            await message.answer(text_chunk)
    else:
        await message.answer(text, parse_mode=None)


