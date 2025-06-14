from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80))
    location = db.Column(db.String(200))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    description = db.Column(db.Text)
    media = db.Column(db.String(200))
    time = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    verified = db.Column(db.Boolean, default=False)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80))
    message = db.Column(db.Text)
    time = db.Column(db.String(80))