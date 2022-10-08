import json
import sqlite3

from flask import request, jsonify
from flask_restx import Resource, Namespace

from app.create_db import db
from app.models import User
from app.functions import get_hash, auth_required, get_user, compare_passwords, generate_tokens
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
        user = db.session.query(User).filter(User.email == get_user()).first()
        if user:
            user.password = "Пароль скрыт в целях безопасности"
            return user_schema.dump(user), 200
        else:
            return "Такого пользователя не существует", 404

    @auth_required
    def patch(self):
        """
        Осуществляет изменение профиля пользователя
        :return: Изменённый профиль пользователя в формате словаря
        """
        patch_data = request.json
        user = db.session.query(User).filter(User.email == get_user()).first()
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

    def delete(self, id):
        user = db.session.query(User).get(id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return "Пользователь удалён", 200
        else:
            return "Такого пользователя не существует", 404
