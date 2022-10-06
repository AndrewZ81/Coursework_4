import sqlite3

from flask import request, jsonify
from flask_restx import Resource, Namespace

from app.create_db import db
from app.models import User
from app.functions import get_hash
from app.schemes import UserSchema

users_ns = Namespace("users")  # Создаём пространство имён для пользователей

# Создаём экземпляры классов сериализации
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@users_ns.route("/")
class UsersView(Resource):
    def get(self):
        users = db.session.query(User).all()
        return users_schema.dump(users), 200

    def post(self):
        post_data = request.json
        user = User(**post_data)
        user.password = get_hash(post_data.get("password"))
        try:
            db.session.add(user)
            db.session.commit()
        except sqlite3.OperationalError:
            db.session.rollback()
            return "Не удалось добавить пользователя", 404
        else:
            response = jsonify(post_data)
            response.headers['location'] = f'/users/{user.id}'
            response.status_code = 201
            return response


@users_ns.route("/<int:id>")
class UserView(Resource):
    def get(self, id):
        user = db.session.query(User).get(id)
        if user:
            return user_schema.dump(user), 200
        else:
            return "Такого пользователя не существует", 404

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
