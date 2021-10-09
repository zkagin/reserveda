# config.py
# Contains configuration variables.

import os

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL").replace(
    "postgres://", "postgresql://"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.getenv("SECRET_KEY")

MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT") or 25)
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS") is not None
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
FULL_EMAIL = os.getenv("FULL_EMAIL")
