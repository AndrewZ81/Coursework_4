import sqlite3

from flask import request, jsonify
from flask_restx import Resource, Namespace

from app.create_db import db
from app.functions import auth_required
from app.models import Director
from app.schemes import DirectorSchema
from constants import ITEMS_PER_PAGE

directors_ns = Namespace("directors")  # Создаём пространство имён для режиссёров

# Создаём экземпляры классов сериализации
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


@directors_ns.route("/")  # Создаём маршрут выборки всех режиссёров и добавления режиссёра
class DirectorsView(Resource):
    @auth_required
    def get(self):
        """
        Осуществляет выборку режиссёров
        :return: Список режиссёров (полностью или постранично)
        """
        page_number = request.args.get("page")
        if page_number:
            page = db.session.query(Director).paginate(page=int(page_number), per_page=ITEMS_PER_PAGE).items
            return directors_schema.dump(page), 200
        else:
            directors = db.session.query(Director).all()
            return directors_schema.dump(directors), 200

    @auth_required
    def post(self):
        """
        Создаёт и сохраняет нового режиссёра
        :return: Сохраняет экземпляр класса Director в таблицу directors БД
        """
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


@directors_ns.route("/<int:id>")  # Создаём маршрут выборки, изменения и удаления режиссёра
class DirectorView(Resource):
    @auth_required
    def get(self, id):
        """
        Осуществляет выборку режиссёра
        :param id: Ключ выборки режиссёра
        :return: Режиссер в формате словаря
        """
        director = db.session.query(Director).get(id)
        if director:
            return director_schema.dump(director), 200
        else:
            return "Такого режиссёра не существует", 404

    @auth_required
    def put(self, id):
        """
        Осуществляет полное редактирование режиссёра
        :param id: Ключ выборки режиссёра
        :return: Сохраняет изменённый экземпляр класса Director в таблицу directors БД
        """
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
        """
        Осуществляет удаление режиссёра
        :param id: Ключ выборки режиссёра
        :return: Удаляет экземпляр класса Director из таблицы directors БД
        """
        director = db.session.query(Director).get(id)
        if director:
            db.session.delete(director)
            db.session.commit()
            return "Режиссёр удалён", 200
        else:
            return "Такого режиссёра не существует", 404
