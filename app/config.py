# Создаём класс конфигурации приложения
class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///movies.db"
    RESTX_JSON = {"ensure_ascii": False}
    DEBUG = True
