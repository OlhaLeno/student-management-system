from flask import Flask

from app.dal.database import db
from app.pl.routes import api


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"

    db.init_app(app)

    app.register_blueprint(api)

    return app
