import sqlite3

from flask import request, jsonify
from flask_restx import Resource, Namespace

from app.create_db import db
from app.functions import auth_required, admin_required
from app.models import Genre
from app.schemes import GenreSchema

genres_ns = Namespace("genres")  # Создаём пространство имён для жанров

# Создаём экземпляры классов сериализации
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@genres_ns.route("/")
class GenresView(Resource):
    @auth_required
    def get(self):
        genres = db.session.query(Genre).all()
        return genres_schema.dump(genres), 200

    @admin_required
    def post(self):
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


@genres_ns.route("/<int:id>")
class GenreView(Resource):
    @auth_required
    def get(self, id):
        genre = db.session.query(Genre).get(id)
        if genre:
            return genre_schema.dump(genre), 200
        else:
            return "Такого жанра не существует", 404

    @admin_required
    def put(self, id):
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

    @admin_required
    def delete(self, id):
        genre = db.session.query(Genre).get(id)
        if genre:
            db.session.delete(genre)
            db.session.commit()
            return "Жанр удалён", 200
        else:
            return "Такого жанра не существует", 404
