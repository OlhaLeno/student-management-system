from datetime import time

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError

from app.dal.database import db


def make_api(name, import_name):
    api = Blueprint(name, import_name, url_prefix="/api")

    @api.errorhandler(ValueError)
    def handle_validation_error(error):
        db.session.rollback()
        return {"error": str(error)}, 400

    @api.errorhandler(LookupError)
    def handle_not_found(error):
        db.session.rollback()
        return {"error": str(error)}, 404

    @api.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        db.session.rollback()
        return {"error": "Порушення цілісності даних."}, 409

    return api


def get_data():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Очікуються дані у форматі JSON.")
    return data


def positive_int(value, field):
    if type(value) is not int or value < 1:
        raise ValueError(f"Некоректне значення поля «{field}».")
    return value


def query_int(field):
    value = request.args.get(field)
    if value is None:
        return None
    try:
        value = int(value)
    except ValueError:
        raise ValueError(f"Некоректний параметр «{field}».") from None
    return positive_int(value, field)


def parse_time(value, field):
    if not isinstance(value, str):
        raise ValueError(f"Вкажіть коректний час у полі «{field}».")
    try:
        if len(value) not in (5, 8) or value[2] != ":":
            raise ValueError
        if len(value) == 8 and value[5] != ":":
            raise ValueError
        result = time.fromisoformat(value)
        if result.tzinfo is not None:
            raise ValueError
        return result
    except ValueError:
        raise ValueError(
            f"Поле «{field}» має містити час у форматі HH:MM або HH:MM:SS."
        ) from None
