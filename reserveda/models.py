# models.py
# Contains the model representations for all Reserveda objects. These models are then
# reflected in the database structure through Flask-SQLAlchemy.

from datetime import datetime
from reserveda import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from time import time
import jwt
from reserveda import app


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    users = db.relationship("User", backref="group", lazy=True)
    items = db.relationship("Item", backref="group", lazy=True)
    events = db.relationship("Event", backref="group", lazy=True)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)
    events = db.relationship("Event", backref="user", lazy=True)
    owned_items = db.relationship("Item", backref="user", lazy=True)
    waitlists = db.relationship("Waitlist", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])[
                "reset_password"
            ]
        except Exception:
            return
        return User.query.get(id)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    comment = db.Column(db.String(80), nullable=True)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    events = db.relationship("Event", backref="item", lazy=True)
    waitlists = db.relationship("Waitlist", backref="item", lazy=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(80), nullable=False)
    comment = db.Column(db.String(80), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)


class Waitlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comment = db.Column(db.String(80), nullable=True)
