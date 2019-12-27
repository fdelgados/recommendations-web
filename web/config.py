import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DB_USER = 'bc0e0e4f733dda'
    DB_PASSWORD = '00f61efe'
    DB_NAME = 'heroku_8149febc614deb5'
    DB_HOST = 'eu-cdbr-west-02.cleardb.net'
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}/{}'.format(DB_USER,
                                                           DB_PASSWORD,
                                                           DB_HOST,
                                                           DB_NAME)


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DB_USER = 'bc0e0e4f733dda'
    DB_PASSWORD = '00f61efe'
    DB_NAME = 'heroku_8149febc614deb5'
    DB_HOST = 'eu-cdbr-west-02.cleardb.net'
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}/{}'.format(DB_USER,
                                                           DB_PASSWORD,
                                                           DB_HOST,
                                                           DB_NAME)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
