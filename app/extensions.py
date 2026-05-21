from authlib.integrations.flask_client import OAuth
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_pymongo import PyMongo
from werkzeug.local import LocalProxy


mongo = PyMongo()
db = LocalProxy(lambda: mongo.db)
bcrypt = Bcrypt()
login_manager = LoginManager()
oauth = OAuth()
github = LocalProxy(lambda: oauth.create_client("github"))
google = LocalProxy(lambda: oauth.create_client("google"))
