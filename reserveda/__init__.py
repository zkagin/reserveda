from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "sdpifmauewf7a8efon2373"
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = "index"

from reserveda import models, routes  # noqa


@login.user_loader
def load_user(id):
    return models.User.query.get(int(id))
