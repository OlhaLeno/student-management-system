
from app.dal.database import db


def validate_text(value, field_name, max_length):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Заповніть поле «{field_name}».")

    value = value.strip()

    if len(value) > max_length:
        raise ValueError(
            f"Поле «{field_name}» не може перевищувати "
            f"{max_length} символів."
        )

    return value


def get_required(model, record_id, message):
    record = db.session.get(model, record_id)

    if record is None:
        raise LookupError(message)

    return record


def commit():
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
