from dataclasses import dataclass
from typing import Optional, Union
from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply


@dataclass
class Menu:

    """
    Класс реализует меню: текстовое сообщение и клавиатуру (кнопки)
    """

    text: str
    keyboard: Optional[
            Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]
        ] = None

    async def send_menu(self, message: Message, text: str = None):
        """
        Метод отправляет меню (текст и клавиатуру) в ответ на сообщение пользователя.

        :param message: сообщение от пользователя
        :param text: текст меню (по умолчанию self.text)
        :return:
        """

        await message.answer(text or self.text, reply_markup=self.keyboard)


#  Главное меню, возникающее при команде /start
main = Menu('Пришлите PDF-файл или изображение (убрав галочку "Сжать изображение"), а я распознаю текст')
