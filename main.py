from flask import Flask
from flask_restx import Api

from app.config import Config
from app.create_db import db
from app.views.movies import movies_ns
from app.views.genres import genres_ns
from app.views.directors import directors_ns
from app.views.users import users_ns
from app.views.auth import auth_ns


def create_app(config_obj):
    """
    Создаёт экземпляр класса Flask и конфигурирует его
    :param config_obj: Объект конфигурации экземпляра класса Flask
    :return: Экземпляр класса Flask
    """
    application = Flask(__name__)
    application.config.from_object(config_obj)
    application.app_context().push()
    create_extensions(application)
    return application


def create_extensions(flask_app):
    """
    Создаёт расширения экземпляра класса Flask и конфигурирует их
    :param flask_app: Экземпляр класса Flask
    :return:
    """
    db.init_app(flask_app)
    api = Api(flask_app)
    api.add_namespace(movies_ns)
    api.add_namespace(directors_ns)
    api.add_namespace(genres_ns)
    api.add_namespace(users_ns)
    api.add_namespace(auth_ns)


app_config = Config()  # Создаём экземпляр класса конфигурации приложения
app = create_app(app_config)  # Создаём наше приложение Flask

if __name__ == "__main__":  # Точка входа в наше приложение Flask
    app.run()
