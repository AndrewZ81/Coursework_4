import json

from flask import request, jsonify
from flask_restx import Resource, Namespace

from app.create_db import db
from app.models import User
from app.functions import compare_passwords, generate_tokens, regenerate_tokens, check_token

auth_ns = Namespace("auth")  # Создаём пространство имён аутентификации


@auth_ns.route("/")  # Создаём маршрут аутентификации
class AuthView(Resource):
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

    def put(self):
        put_data = request.json
        token = put_data.get("refresh_token")
        if check_token(token):
            response = jsonify(regenerate_tokens(token))
            response.status_code = 201
            return response
        else:
            return "Ошибка декодирования токена", 404
