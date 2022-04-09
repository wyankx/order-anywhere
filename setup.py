import os
import datetime

from flask import Flask
from flask_restful import Api

from data import db_session

# Will not work on Heroku, but needed for tests
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

db_session.global_init(os.environ.get('DATABASE_URL'))

from data.db_session import get_session


from flask_socketio import SocketIO

app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
print(f' * SECRET_KEY: {os.environ.get("SECRET_KEY")}')
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['SQLALCHEMY_POOL_SIZE'] = 20

socketio = SocketIO(app, async_mode='threading')
