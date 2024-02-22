import asyncio
import logging
from aiogram import types, F, Router
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, ErrorEvent, Message
from .middlewares import ChatActionMiddleware
from ..OCR.converter import image_to_text, convert_pdf
from ..interface import menu
from .utils import split_and_send, DocumentManager


logger = logging.getLogger()

router = Router()

#  Подключаем мидлварь для установки статуса (например, "печатает") во время длительных операций
router.message.middleware(ChatActionMiddleware())


#  обработка ошибок хендлеров роутера
@router.error(F.update.message.as_('message'))
async def error_handler(event: ErrorEvent, message: Message):
    logger.critical('Error caused by %s', event.exception, exc_info=True)
    await message.answer('Во время запроса произошла ошибка, попробуйте ещё раз')


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    """
    Функция сбрасывает позицию и связанные данные пользователя (FSM) и отправляет главное меню.
    Команда /start может использоваться как сброс.
    """

    #  Сброс данных
    await state.clear()

    #  Отправка главного меню
    await menu.main.send_menu(message)


@router.message(F.document.mime_type == 'application/pdf', flags={'long_operation': 'upload_document'})
async def pdf_converter(message: types.Message):

    """Функция реагирует на присланный pdf-файл, распознаёт текст и конвертирует в .docx"""

    await message.answer('Документ получен, обработка в процессе. Пожалуйста, подождите...')

    #  имя присланного файла
    doc_name = message.document.file_name.split('.')[0]

    async with DocumentManager(message) as file_bytes_io:  # неявное скачивание присланного документа в виде байтов

        # распознание и конвертация
        await asyncio.to_thread(convert_pdf, file_bytes_io)

        # подготовка к отправке распознанного текста
        document = BufferedInputFile(file_bytes_io.getvalue(), filename=f'{doc_name}.docx')

    # отправка готового документа
    await message.answer_document(document)


@router.message(F.document.mime_type.contains('image'), flags={'long_operation': 'typing'})
async def img_to_text(message: types.Message):
    """Функция реагирует на присланный файл изображения, распознаёт текст и отправляет его текст в чат"""

    await message.answer('Картинка получена, обработка в процессе. Пожалуйста, подождите...')

    async with DocumentManager(message) as file_bytes_io:  # неявное скачивание присланного документа в виде байтов

        #  распознание картинки в список строк
        sentences = await asyncio.to_thread(image_to_text, file_bytes_io.getvalue())

    text = ' '.join(sentences)

    if not text or text.isspace():
        text = 'Ой, ничего не распозналось'

    #  Длина распознанного текста может превышать лимит телеграма (4096 символов на момент 18.02.2024)
    #  Поэтому отправляем сообщение частями <= 4096 символов
    await split_and_send(message, text)


@router.message(F.photo)
async def no_photo(message: types.Message):
    """Функция срабатывает, когда боту присылают картинку не в виде файла"""

    await message.answer('Пожалуйста, отправьте изображение как файл (это повысит качество работы).'
                         '\n\nПК: при загрузке файла уберите галочку "Сжать изображение".'
                         '\n\nСмартфон: нажмите значок "Скрепка" - Файл - Выберите изображение.')


#  Важно оставить эту функцию (хендлер) в конце.
#  Если переместить в самый верх, эта функция будет срабатывать на любое новое событие/сообщение/документ.
@router.message()
async def unknown_command(message: types.Message):
    """Функция срабатывает, когда ни одна команда не распознана (не сработал ни один фильтр выше определённых функций"""
    await message.answer('Неизвестная команда')
