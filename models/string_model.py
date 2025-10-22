from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class StringAnalysis(db.Model):
    __tablename__ = "string_analysis"

    id = db.Column(db.String(64), primary_key=True)
    value= db.Column(db.String, nullable=False, unique=True)
    properties = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<StringAnalysis {self.value}>"