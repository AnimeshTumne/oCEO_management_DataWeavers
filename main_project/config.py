class Config:
    SECRET_KEY = 'mySecretKey'
    SQLALCHEMY_DATABASE_URI = 'mysql://oceoAdmin:oceoAdmin@localhost/oceo_management'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = '127.0.0.1:5000'
