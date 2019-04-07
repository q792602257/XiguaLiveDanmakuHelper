from datetime import datetime
from sqlalchemy import func
from .DataBase import db


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(50))
    is_upload = db.Column(db.Integer(1), server_default=0, default=0)
    create_time = db.Column(db.TIMESTAMP, server_default=func.now(), default=datetime.now())
