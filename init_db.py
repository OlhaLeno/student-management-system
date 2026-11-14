
from sqlalchemy import inspect

from app import create_app
from app.dal.database import db
from app.dal import models


app = create_app()

with app.app_context():
    db.create_all()

    tables = inspect(db.engine).get_table_names()

    print("Database initialized successfully!")
    print("Created tables:", ", ".join(tables))
