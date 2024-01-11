from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.secretKey
app.config['MAX_CONTENT_LENGTH'] = Config.maxFileSize * 1024 * 1024
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)
loginManager = LoginManager(app)
loginManager.login_view = 'login'
loginManager.login_message_category = 'info'

from app import routes