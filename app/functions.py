import base64
import calendar
import datetime
import hashlib
import hmac
import jwt
from flask import request

from constants import JWT_SECRET, JWT_ALGORITHM, PWD_HASH_SALT, PWD_HASH_ITERATIONS


def get_hash(password):
    """
    Создаёт хэш пароля пользователя
    :param password: Пароль пользователя
    :return: Хэш пароля пользователя в виде строки
    """
    hash_digest = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),  # Convert the password to bytes
        PWD_HASH_SALT,
        PWD_HASH_ITERATIONS
    )
    return base64.b64encode(hash_digest)


def compare_passwords(password_hash, other_password):
    """
    Сравнивает переданный и сохранённый пароли пользователя
    :param password_hash: Сохранённый пароль пользователя
    :param other_password: Переданный пароль пользователя
    :return: Булево значение
    """
    entered_password = base64.b64decode(get_hash(other_password))
    saved_password = base64.b64decode(password_hash)
    return hmac.compare_digest(saved_password, entered_password)


def generate_tokens(data):
    """
    Создаёт токены для пользователя
    :param data: Данные пользователя
    :return: Access_token и Refresh_token в формате словаря
    """
    min30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    data["exp"] = calendar.timegm(min30.timetuple())
    access_token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)

    days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
    data["exp"] = calendar.timegm(days130.timetuple())
    refresh_token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)

    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    return tokens

def check_token(token):
    """
    Проверяет токен
    :param token: Токен для проверки
    :return: Булево значение
    """
    try:
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception:
        return False
    else:
        return True


def regenerate_tokens(token):
    """
    Пересоздаёт токены для пользователя
    :param token: Токен Refresh_token
    :return: Access_token и Refresh_token в формате словаря
    """
    data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    min30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    data["exp"] = calendar.timegm(min30.timetuple())
    access_token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)

    days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
    data["exp"] = calendar.timegm(days130.timetuple())
    refresh_token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)

    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    return tokens


def auth_required(func):
    """
    Создает декоратор авторизации пользователя
    :param func: Декорируемая функция
    :return: Декорируемую функцию или сообщение
    """
    def wrapper(*args, **kwargs):
        data = request.headers.get("Authorization")
        if data:
            token = data.split("Bearer ")[-1]
            if check_token(token):
                return func(*args, **kwargs)
            else:
                return "Ошибка декодирования токена", 404
        else:
            return "Вы не авторизованы", 401
    return wrapper
