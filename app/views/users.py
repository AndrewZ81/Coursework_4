import sqlite3

from flask import request, jsonify
from flask_restx import Resource, Namespace

from app.create_db import db
from app.models import User
from app.functions import auth_required, get_user, compare_passwords, get_hash, generate_tokens, get_user_password
from app.schemes import UserSchema

users_ns = Namespace("user")  # Создаём пространство имён для пользователей

# Создаём экземпляры классов сериализации
user_schema = UserSchema()


@users_ns.route("/")
class UsersView(Resource):
    @auth_required
    def get(self):
        """
        Осуществляет выборку пользователя
        :return: Профиль пользователя в формате словаря
        """

        # Получаем пользователя из БД по e-mail из токена
        user = db.session.query(User).filter(User.email == get_user()).first()

        if user:
            user.password = "Пароль скрыт в целях безопасности"
            return user_schema.dump(user), 200
        else:
            return "Такого пользователя не существует", 404

    @auth_required
    def patch(self):
        """
        Осуществляет изменение профиля пользователя (имени, фамилии и любимого жанра)
        :return: Изменённый профиль пользователя в формате словаря
        """

        # Получаем пользователя из БД по e-mail из токена
        user = db.session.query(User).filter(User.email == get_user()).first()

        patch_data = request.json  # Передаем имя, фамилию и любимый жанр
        if user:
            try:
                user.password = "Пароль скрыт в целях безопасности"
                user.name = patch_data.get("name")
                user.surname = patch_data.get("surname")
                user.favorite_genre = patch_data.get("favorite_genre")
                db.session.add(user)
                db.session.commit()
            except sqlite3.OperationalError:
                db.session.rollback()
                return "Не удалось изменить пользователя", 404
            else:
                return user_schema.dump(user), 200
        else:
            return "Такого пользователя не существует", 404

    @auth_required
    def put(self):
        """
        Осуществляет изменение пароля пользователя
        :return: Словарь новых JWT (access_token и refresh_token)
        """

        # Получаем пользователя из БД по e-mail из токена
        user = db.session.query(User).filter(User.email == get_user()).first()

        patch_data = request.json  # Передаём новый пароль

        # Добавляем ключ, содержащий email пользователя, для генерации пары токенов
        patch_data["email"] = user.email

        if user:
            try:
                old_password = get_user_password()  # Получаем старый пароль из токена
                new_password = patch_data.get("password")
                if not new_password:
                    return "Пустой пароль", 404
                elif compare_passwords(user.password, old_password):
                    user.password = get_hash(new_password)
                    db.session.add(user)
                    db.session.commit()
                else:
                    return "Неверный пароль", 404
            except sqlite3.OperationalError:
                db.session.rollback()
                return "Не удалось изменить пользователя", 404
            else:
                response = jsonify(generate_tokens(patch_data))
                response.status_code = 201
                return response
        else:
            return "Такого пользователя не существует", 404
