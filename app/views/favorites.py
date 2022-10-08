from flask_restx import Resource, Namespace

from app.create_db import db
from app.functions import auth_required, get_user
from app.models import favorite, User, Movie

from sqlalchemy import create_engine
from app.config import Config

favorites_ns = Namespace("favorites/movies")  # Создаём пространство имён для избранного


@favorites_ns.route("/<int:movie_id>")  # Создаём маршрут добавления в избранное фильма и его удаления
class FavoritesView(Resource):
    @auth_required
    def post(self, movie_id):
        """
        Cохраняет фильм в избранное
        :return: Создает и сохраняет новую запись в таблицу favorites
        """

        # Получаем пользователя из БД по e-mail из токена
        user = db.session.query(User).filter(User.email == get_user()).first()

        if user:
            movies = db.session.query(Movie).all()
            for i in movies:  # Сверяем ID всех фильмов в БД с переданным ID
                if i.id == movie_id:
                    try:
                        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
                        conn = engine.connect()
                        ins = favorite.insert().values(user_id = user.id, movie_id = movie_id)
                        conn.execute(ins)
                    except Exception:
                        return "Не удалось добавить в избранное", 404
                    else:
                         return "Добавлено в избранное", 200
            return "Фильма с таким ID не существует", 404
        else:
            return "Такого пользователя не существует", 404