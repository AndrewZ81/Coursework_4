import sqlite3

from flask import request, jsonify
from flask_restx import Resource, Namespace

from app.create_db import db
from app.functions import auth_required
from app.models import Director
from app.schemes import DirectorSchema

directors_ns = Namespace("directors")  # Создаём пространство имён для режиссёров

# Создаём экземпляры классов сериализации
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


@directors_ns.route("/")  # Создаём маршрут выборки всех режиссёров и добавления режиссёра
class DirectorsView(Resource):
    @auth_required
    def get(self):
        directors = db.session.query(Director).all()
        return directors_schema.dump(directors), 200

    @auth_required
    def post(self):
        post_data = request.json
        director = Director(**post_data)
        try:
            db.session.add(director)
            db.session.commit()
        except sqlite3.OperationalError:
            db.session.rollback()
            return "Не удалось добавить режиссёра", 404
        else:
            response = jsonify(post_data)
            response.headers['location'] = f'/directors/{director.id}'
            response.status_code = 201
            return response


@directors_ns.route("/<int:id>")
class DirectorView(Resource):
    @auth_required
    def get(self, id):
        director = db.session.query(Director).get(id)
        if director:
            return director_schema.dump(director), 200
        else:
            return "Такого режиссёра не существует", 404

    @auth_required
    def put(self, id):
        put_data = request.json
        director = db.session.query(Director).get(id)
        if director:
            try:
                director.name = put_data.get("name")
                db.session.add(director)
                db.session.commit()
            except sqlite3.OperationalError:
                db.session.rollback()
                return "Не удалось изменить режиссёра", 404
            else:
                return "Режиссёр изменён", 200
        else:
            return "Такого режиссёра не существует", 404

    @auth_required
    def delete(self, id):
        director = db.session.query(Director).get(id)
        if director:
            db.session.delete(director)
            db.session.commit()
            return "Режиссёр удалён", 200
        else:
            return "Такого режиссёра не существует", 404
