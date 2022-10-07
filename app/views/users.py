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

    def post(self):
        post_data = request.json
        user_name = post_data.get("username")
        user_password = post_data.get("password")
        if not user_name:
            return "Пустое имя пользователя", 404
        elif not user_password:
            return "Пустой пароль", 404
        users = db.session.query(User).filter(User.username == user_name).all()
        if not users:
            return "Неверное имя пользователя", 404
        else:
            for i in users:
                if compare_passwords(i.password, user_password):
                    post_data["role"] = i.role
                    response = jsonify(generate_tokens(post_data))
                    response.status_code = 201
                    return response
        return "Неверный пароль", 404


@users_ns.route("/<int:id>")
class UserView(Resource):


    def put(self, id):
        put_data = request.json
        user = db.session.query(User).get(id)
        if user:
            try:
                user.username = put_data.get("username")
                user.password = get_hash(put_data.get("password"))
                user.role = put_data.get("role")
                db.session.add(user)
                db.session.commit()
            except sqlite3.OperationalError:
                db.session.rollback()
                return "Не удалось изменить пользователя", 404
            else:
                return "Пользователь изменён", 200
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
