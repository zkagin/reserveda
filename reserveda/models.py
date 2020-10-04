from reserveda import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    # comment = db.Column(db.String(80), nullable=True)
    events = db.relationship("Event", backref="item", lazy=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(80), nullable=False)
    comment = db.Column(db.String(80), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)
