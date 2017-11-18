import os

# Enable debugging during development
DEBUG = True

# Secret key to use sessions
SECRET_KEY = '\xfb\x13\xdf\xa1@i\xd6>V\xc0\xbf\x8fp\x16#Z\x0b\x81\xeb\x16'

# Create in-memory database
basedir = os.path.abspath(os.path.dirname(__file__))

# Flask-Security config
SECURITY_URL_PREFIX = "/admin"
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SALT = "B0E809D91551B3982AFE66F5BDE732531C7E3AEFA8874A17379ABF05985FB242"

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"
SECURITY_REGISTER_URL = "/register/"

# Flask-Security features
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Custom pages
SECURITY_LOGIN_USER_TEMPLATE = 'login.html'
SECURITY_REGISTER_USER_TEMPLATE = 'register.html'
