class Config:
    SECRET_KEY = 'super_secret_key'

    # Flask-MySQLdb Settings
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '12345'
    MYSQL_DB = 'concert_db'
    MYSQL_PORT = 3307

    # Uploads
    UPLOAD_FOLDER = "static/posters"

    # Email
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "lewiekltm@gmail.com"
    MAIL_PASSWORD = "opbm wplh wtzo zbli"
    MAIL_DEFAULT_SENDER = ("Concert Tickets", MAIL_USERNAME)
