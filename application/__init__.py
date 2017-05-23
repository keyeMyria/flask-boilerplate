import os

from flask import Flask

from config import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('CONFIG', 'production')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from application.modules.home import home
    app.register_blueprint(home)

    return app
