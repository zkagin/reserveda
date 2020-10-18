from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_talisman import Talisman
from .momentjs import momentjs
from reserveda import config

# Basic configuration of the application.
app = Flask(__name__)
app.config.from_object(config)
app.jinja_env.globals["momentjs"] = momentjs
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "index"

# Configure Talisman
csp = {
    "default-src": [
        "'self'",
        "'unsafe-inline'",
        "cdnjs.cloudflare.com",
        "stackpath.bootstrapcdn.com",
    ]
}

Talisman(app, content_security_policy=csp)

from reserveda import models, routes  # noqa


# Helper function for flask_login to understand when a user is logged in.
@login.user_loader
def load_user(id):
    return models.User.query.get(int(id))
