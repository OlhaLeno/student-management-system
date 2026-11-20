from flask import Flask
from app.pl.university_routes import university_api
from app.pl.student_routes import student_api
from app.pl.teaching_routes import teaching_api
from app.pl.schedule_routes import schedule_api
from app.pl.grade_routes import grade_api
from app.pl.report_routes import report_api
from app.dal.database import db
from app.pl.routes import api
from app.pl.web_routes import web


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"

    db.init_app(app)

    app.register_blueprint(api)
    app.register_blueprint(university_api)
    app.register_blueprint(student_api)
    app.register_blueprint(teaching_api)
    app.register_blueprint(schedule_api)
    app.register_blueprint(grade_api)
    app.register_blueprint(report_api)
    app.register_blueprint(web)
    app.json.ensure_ascii = False

    return app
