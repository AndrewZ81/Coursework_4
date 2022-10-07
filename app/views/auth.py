import json
import sqlite3

from flask import request, jsonify
from flask_restx import Resource, Namespace

from app.create_db import db
from app.models import User
from app.functions import compare_passwords, generate_tokens, regenerate_tokens, check_token, get_hash

auth_ns = Namespace("auth")  # Создаём пространство имён аутентификации


@auth_ns.route("/register")  # Создаём маршрут регистрации пользователя
class AuthView(Resource):
    def post(self):
        """
        Создаёт нового пользователя
        :return: Сохраняет экземпляр класса User в таблицу users БД
        """
        post_data = request.json
        email = post_data.get("email")
        user_password = post_data.get("password")
        user = User(**post_data)
        if not email:
            return "Пустой адрес электронной почты", 404
        elif not user_password:
            return "Пустой пароль", 404
        user.password = get_hash(post_data.get("password"))
        try:
            db.session.add(user)
            db.session.commit()
        except sqlite3.OperationalError:
            db.session.rollback()
            return "Не удалось добавить пользователя", 404
        else:
            response = jsonify(post_data)
            response.headers['location'] = f'/auth/register/{user.id}'
            response.status_code = 201
            return response


@auth_ns.route("/login")  # Создаём маршрут аутентификации и идентификации пользователя
class AuthView(Resource):
    def post(self):
        """
        Создаёт токен доступа и токен обновления токенов
        :return: Словарь JWT (access_token и refresh_token)
        """
        post_data = request.json
        email = post_data.get("email")
        user_password = post_data.get("password")
        if not email:
            return "Пустой адрес электронной почты", 404
        elif not user_password:
            return "Пустой пароль", 404
        user = db.session.query(User).filter(User.email == email).first()
        if not user:
            return "Неверный адрес электронной почты", 404
        else:
            if compare_passwords(user.password, user_password):
                response = jsonify(generate_tokens(post_data))
                response.status_code = 201
                return response
            return "Неверный пароль", 404


    def put(self):
        """
        Пересоздаёт токен доступа и токен обновления токенов
        :return: Словарь JWT (access_token и refresh_token)
        """
        put_data = request.json
        token = put_data.get("refresh_token")
        if check_token(token):
            response = jsonify(regenerate_tokens(token))
            response.status_code = 201
            return response
        else:
            return "Ошибка декодирования токена", 404
