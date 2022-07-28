import os


class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("MY_FLASK_SECRET")
    SECRET_KEY = "do_not_ask"
    SECURITY_PASSWORD_SALT = "do_not_ask_me"

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://djose1164:Kirito08.@db4free.net/test_cara"
    )


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_ECHO = False
