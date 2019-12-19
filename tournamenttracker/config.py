import os


class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'

    # 3 slashes are a relative path from the current file
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'

    # MAIL_SERVER = 'smtp.googlemail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('EMAIL_USER')
    # MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
