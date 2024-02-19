from asyncio import run
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from core.handlers import router
from os import getenv
from core.config import set_logging


async def start_bot(token: str,
                    logging_file: str,
                    logging_format: str,
                    parse_mode: str,
                    drop_pending_updates: bool = True):

    """
    Функция конфигурирует запускает бота.

    :param token: токе бота, полученный у @BotFather
    :param logging_file: путь к файлу для логирования ошибок
    :param logging_format: формат логирования
    :param parse_mode: разметка сообщений в телеграм
    :param drop_pending_updates: пропускать ли обновления, полученные в период незапущенного бота
    :return:
    """

    set_logging(logging_file, logging_format)

    bot = Bot(token=token, parse_mode=parse_mode)
    await bot.delete_webhook(drop_pending_updates=drop_pending_updates)
    dp = Dispatcher()
    dp.include_routers(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    token = getenv('tg_bot_token')
    logging_file = 'bot/errors.txt'
    logging_format = '%(asctime)s - %(levelname)s - %(message)s'

    run(start_bot(token, logging_file, logging_format, ParseMode.HTML, drop_pending_updates=True))
