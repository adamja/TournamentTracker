import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', default='5791628bb0b13ce0c676dfde280ba245')

    # --- DATABASE
    # 3 slashes are a relative path from the current file
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI",
                                             default='sqlite:///' + os.path.join(basedir, 'data/db/app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- MAIL
    # MAIL_SERVER = 'smtp.googlemail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('EMAIL_USER')
    # MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
