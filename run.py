import os
from app import create_app, db
from config import config

env = os.environ.get('ENV', 'default')

application = create_app(config[env])


if __name__ == '__main__':
    application.run()
