import sqlite3

from flask import request, jsonify
from flask_restx import Resource, Namespace

from app.create_db import db
from app.functions import auth_required
from app.models import Genre
from app.schemes import GenreSchema
from constants import ITEMS_PER_PAGE

genres_ns = Namespace("genres")  # Создаём пространство имён для жанров

# Создаём экземпляры классов сериализации
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@genres_ns.route("/")  # Создаём маршрут выборки списка жанров и создания жанра
class GenresView(Resource):
    @auth_required
    def get(self):
        """
        Осуществляет выборку жанров
        :return: Список жанров (полностью или постранично)
        """
        page_number = request.args.get("page")
        if page_number:
            page = db.session.query(Genre).paginate(page=int(page_number), per_page=ITEMS_PER_PAGE).items
            return genres_schema.dump(page), 200
        else:
            genres = db.session.query(Genre).all()
            return genres_schema.dump(genres), 200

    @auth_required
    def post(self):
        """
        Создаёт и сохраняет новый жанр
        :return: Сохраняет экземпляр класса Genre в таблицу genres БД
        """
        post_data = request.json
        genre = Genre(**post_data)
        try:
            db.session.add(genre)
            db.session.commit()
        except sqlite3.OperationalError:
            db.session.rollback()
            return "Не удалось добавить жанр", 404
        else:
            response = jsonify(post_data)
            response.headers['location'] = f'/genres/{genre.id}'
            response.status_code = 201
            return response


@genres_ns.route("/<int:id>")  # Создаём маршрут выборки, изменения и удаления жанра
class GenreView(Resource):
    @auth_required
    def get(self, id):
        """
        Осуществляет выборку жанра
        :param id: Ключ выборки жанра
        :return: Жанр в формате словаря
        """
        genre = db.session.query(Genre).get(id)
        if genre:
            return genre_schema.dump(genre), 200
        else:
            return "Такого жанра не существует", 404

    @auth_required
    def put(self, id):
        """
        Осуществляет полное редактирование жанра
        :param id: Ключ выборки жанра
        :return: Сохраняет изменённый экземпляр класса Genre в таблицу genres БД
        """
        put_data = request.json
        genre = db.session.query(Genre).get(id)
        if genre:
            try:
                genre.name = put_data.get("name")
                db.session.add(genre)
                db.session.commit()
            except sqlite3.OperationalError:
                db.session.rollback()
                return "Не удалось изменить жанр", 404
            else:
                return "Жанр изменён", 200
        else:
            return "Такого жанра не существует", 404

    @auth_required
    def delete(self, id):
        """
        Осуществляет удаление жанра
        :param id: Ключ выборки жанра
        :return: Удаляет экземпляр класса Genre из таблицы genres БД
        """
        genre = db.session.query(Genre).get(id)
        if genre:
            db.session.delete(genre)
            db.session.commit()
            return "Жанр удалён", 200
        else:
            return "Такого жанра не существует", 404
