from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .momentjs import momentjs
from reserveda import config

app = Flask(__name__)
app.config.from_object(config)
app.jinja_env.globals["momentjs"] = momentjs
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = "index"

from reserveda import models, routes  # noqa


@login.user_loader
def load_user(id):
    return models.User.query.get(int(id))
