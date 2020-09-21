import random
from PIL import Image


def generate_random_string(
    length=32,
    allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """
    Функция генерации случайной строки.
    *   Аргументы:
    *   length - длина возвращаемой строки (по умолчанию: 32)
    *   allowed_chars - строка, содержащая допустимые символы
    """
    string = ''
    for i in range(length):
        string += random.choice(allowed_chars)
    return string


def crop_image_rect(image, max_size=None):
    """
    Функция обрезки картинки до квадрата без полей.
    *   Аргументы:
    *   image - изображение, объект класса PIL.Image
    *   max_size - максимальное разрешение картинки на выходе(одно число, так как картинка на выходе квадратная)
    *
    *   Возвращает: PIL.Image
    """
    if not max_size:
        max_size = min(image.width, image.height)
    halfWidth = image.width // 2        # Половина ширины картинки
    halfHeight = image.height // 2      # Половина высоты картинки
    # Обрезаем картинку до квадрата в центре
    if image.width > image.height:
        image = image.crop((
            halfWidth - halfHeight, 0,
            halfWidth + halfHeight, image.height
        ))
    else:
        image = image.crop((
            0, halfHeight - halfWidth,
            image.width, halfHeight + halfWidth
        ))
    # Подгоняем размер картинки до максимального и возвращаем
    return image.resize((max_size, max_size), Image.ANTIALIAS)
