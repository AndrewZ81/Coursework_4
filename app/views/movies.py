import sqlite3
from flask import jsonify
from flask import request
from flask_restx import Resource, Namespace

from app.create_db import db
from app.models import Movie
from app.schemes import MovieSchema

from app.functions import auth_required

movies_ns = Namespace("movies")  # Создаём пространство имён для фильмов

# Создаём экземпляры классов сериализации
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

# Создаём маршрут выборки всех фильмов, фильмов по режиссёру/жанру/году и добавления фильма
@movies_ns.route("/")
class MoviesView(Resource):
    @auth_required
    def get(self):
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")
        year = request.args.get("year")
        if director_id:
            movies = db.session.query(Movie).filter(Movie.director_id == int(director_id)).all()
            if movies:
                return movies_schema.dump(movies), 200
            else:
                return "Такого режиссёра не существует", 404
        elif genre_id:
            movies = db.session.query(Movie).filter(Movie.genre_id == int(genre_id)).all()
            if movies:
                return movies_schema.dump(movies), 200
            else:
                return "Такого жанра не существует", 404
        elif year:
            movies = db.session.query(Movie).filter(Movie.year == int(year)).all()
            if movies:
                return movies_schema.dump(movies), 200
            else:
                return "Фильмов такого года не существует", 404
        else:
            movies = db.session.query(Movie).all()
            return movies_schema.dump(movies), 200

    @auth_required
    def post(self):
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
        movie = db.session.query(Movie).get(id)
        if movie:
            return movie_schema.dump(movie), 200
        else:
            return "Такого фильма не существует", 404

    @auth_required
    def put(self, id):
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
        movie = db.session.query(Movie).get(id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return "Фильм удалён", 200
        else:
            return "Такого фильма не существует", 404
