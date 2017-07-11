from flask import Flask

from config import config


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from application.controller.home import home
    app.register_blueprint(home)

    return app
