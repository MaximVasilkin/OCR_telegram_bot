from functools import lru_cache
from io import BytesIO
import cv2
import easyocr
import fitz
import numpy as np
from pdf2docx import Converter
from bot.core.config import LANGUAGES


@lru_cache(maxsize=5)
def get_reader(languages: tuple) -> easyocr.Reader:
    """
    Функция кеширует и возвращает объект распознания изображений.

    :param languages: список распознаваемых языков.
    :return: объект распознания изображений.
    """

    return easyocr.Reader(list(languages))


def pre_process_image(image: bytes) -> bytes:
    """
    Функция предобрабатки изображения с целью повысить качество распознавания текста.

    :param image: байты изображения.
    :return: байты изображения.
    """

    # Распаковка массива байтов в изображение
    image_array = np.frombuffer(image, dtype=np.uint8)

    #  обрабатываем изображение
    image = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)  # Перевод в Ч/Б

    # TODO: upscale, denoising, other enhancing

    # подготавливаем обработанное изображение
    _, buffer = cv2.imencode('.jpg', image)  # Кодирование изображения в памяти

    # Преобразование буфера в массив байтов
    binary_image_bytes = buffer.tobytes()

    return binary_image_bytes


def image_to_text(image: bytes, languages: tuple = LANGUAGES, detail: int = 0) -> list[str]:
    """
    Функция распознаёт текст с изображения.

    :param image: байты изображения.
    :param languages: кортеж распознаваемых языков.
    :param detail: 0 - плоское представление (только текст), 1 - добавить метаданные (координаты распознанного и т.д.)
    :return: список распознанных данных.
    """
    reader = get_reader(languages)
    return reader.readtext(image, detail=detail)


def pdf_to_docx(file_bytes: bytes, bytes_io: BytesIO) -> bool:
    """
    Функция конвертирует pdf в docx и сохраняет результат в буфер.

    :param file_bytes: pdf-файл в виде байтов.
    :param bytes_io: буфер
    :return:
    """

    cv = Converter(stream=file_bytes)
    try:
        cv.convert(bytes_io)
        return True
    finally:
        cv.close()


def convert_pdf(output_bytesio: BytesIO):
    """
    Основная функция, которая заменяет все изображения в pdf-файле на текст, распознанный с них.
    Затем, функция конвертирует pdf в docx и сохраняет результат в буфер.

    :param output_bytesio: буфер.
    :return:
    """

    doc = fitz.open('pdf', output_bytesio.getvalue())
    try:
        for page in doc:
            for image_info in page.get_images():
                # тут координаты прямоугольника с изображением
                bbox = page.get_image_bbox(image_info[-2])

                #  получаем картинку
                image_xref = image_info[0]
                image = doc.extract_image(image_xref)
                image_bytes = image['image']

                #  обрабатываем изображение с целью улучшить качество расознания текста
                pre_proccessed = pre_process_image(image_bytes)

                #  получаем текст с картинки
                text_from_image = image_to_text(pre_proccessed)
                text_from_image = " ".join(text_from_image)

                #  заменяем картинку на текст
                page.clean_contents()
                page.delete_image(image_xref)
                page.insert_htmlbox(bbox, text_from_image)

        #  сохраняем документ
        doc.save(output_bytesio)
    finally:
        doc.close()

    #  конвертируем документ
    pdf_to_docx(output_bytesio.getvalue(), output_bytesio)
