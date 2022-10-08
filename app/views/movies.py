import sqlite3
from flask import jsonify
from flask import request
from flask_restx import Resource, Namespace

from app.create_db import db
from app.models import Movie
from app.schemes import MovieSchema

from app.functions import auth_required
from constants import ITEMS_PER_PAGE

movies_ns = Namespace("movies")  # Создаём пространство имён для фильмов

# Создаём экземпляры классов сериализации
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

# Создаём маршрут выборки всех фильмов, сортировки фильмов по новизне и добавления фильма
@movies_ns.route("/")
class MoviesView(Resource):
    @auth_required
    def get(self):
        """
        Осуществляет выборку фильмов и их сортировку
        :return: Список фильмов (полностью или постранично, отсортированный или нет)
        """
        page_number = request.args.get("page")
        status = request.args.get("status")
        if page_number and status == "new":
            page = db.session.query(Movie).order_by(Movie.year.desc()).\
                paginate(page=int(page_number), per_page=ITEMS_PER_PAGE).items
            return movies_schema.dump(page), 200
        elif page_number:
            page = db.session.query(Movie).paginate(page=int(page_number), per_page=ITEMS_PER_PAGE).items
            return movies_schema.dump(page), 200
        elif status == "new":
            movies = db.session.query(Movie).order_by(Movie.year.desc())
            return movies_schema.dump(movies), 200
        else:
            movies = db.session.query(Movie).all()
            return movies_schema.dump(movies), 200

    @auth_required
    def post(self):
        """
        Создаёт и сохраняет новый фильм
        :return: Сохраняет экземпляр класса Movie в таблицу movies БД
        """
        post_data = request.json
        movie = Movie(**post_data)
        try:
            db.session.add(movie)
            db.session.commit()
        except sqlite3.OperationalError:
            db.session.rollback()
            return "Не удалось добавить фильм", 404
        else:
            response = jsonify(post_data)
            response.headers['location'] = f'/movies/{movie.id}'
            response.status_code = 201
            return response


@movies_ns.route("/<int:id>")  # Создаём маршрут выборки, изменения и удаления одного фильма
class MovieView(Resource):
    @auth_required
    def get(self, id):
        """
        Осуществляет выборку фильма
        :param id: Ключ выборки фильма
        :return: Фильм в формате словаря
        """
        movie = db.session.query(Movie).get(id)
        if movie:
            return movie_schema.dump(movie), 200
        else:
            return "Такого фильма не существует", 404

    @auth_required
    def put(self, id):
        """
        Осуществляет полное редактирование строки фильма
        :param id: Ключ выборки фильма
        :return: Сохраняет изменённый экземпляр класса Movie в таблицу movies БД
        """
        put_data = request.json
        movie = db.session.query(Movie).get(id)
        if movie:
            try:
                movie.title = put_data.get("title")
                movie.description = put_data.get("description")
                movie.trailer = put_data.get("trailer")
                movie.year = put_data.get("year")
                movie.rating = put_data.get("rating")
                movie.genre_id = put_data.get("genre_id")
                movie.director_id = put_data.get("director_id")
                db.session.add(movie)
                db.session.commit()
            except sqlite3.OperationalError:
                db.session.rollback()
                return "Не удалось изменить фильм", 404
            else:
                return "Фильм изменён", 200
        else:
            return "Такого фильма не существует", 404

    @auth_required
    def delete(self, id):
        """
        Осуществляет удаление строки фильма
        :param id: Ключ выборки фильма
        :return: Удаляет экземпляр класса Movie из таблицы movies БД
        """
        movie = db.session.query(Movie).get(id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return "Фильм удалён", 200
        else:
            return "Такого фильма не существует", 404
