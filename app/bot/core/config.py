import logging


def set_logging(file: str, format: str, type: int = logging.ERROR):

    """
    Настройка логирования.

    :param file: путь к файлу для логирования ошибок
    :param format: формат логирования
    :param type: уровень логирования
    :return:
    """

    logger = logging.getLogger()
    logger.setLevel(type)
    handler = logging.FileHandler(file)
    handler.setLevel(type)
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


#  телеграм лимит символов в одном сообщении
CHAR_LIMIT = 4096

#  распознаваемые языки
LANGUAGES = ('ru', 'en')
