import os
import datetime
import sqlite3

from flask import Flask, render_template, abort, make_response
from flask_login import LoginManager, current_user
from flask_wtf import CSRFProtect

from data import db_session

# Will not work on Heroku, but needed for tests
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

if __name__ == '__main__':
    db_session.global_init(os.environ.get('DATABASE_URL'))

from data.db_session import get_session

import api
from blueprints import settings
from blueprints import accounts
from blueprints import organisations_settings
from blueprints import menus_settings
from blueprints import restaurant_settings
from blueprints import search
from blueprints import order

from data.models.profile_types import ProfileType
from data.models.users import User
from data.models.restaurants import Restaurant
from data.models.menu_items import MenuItem
from flask_socketio import SocketIO


app = api.app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
print(f' * SECRET_KEY: {os.environ.get("SECRET_KEY")}')
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['SQLALCHEMY_POOL_SIZE'] = 20

login_manager = LoginManager()
login_manager.init_app(app)

socketio = SocketIO(app)


@app.teardown_appcontext
def shutdown_session(exception=None):
    get_session().remove()


# Error handlers
@app.errorhandler(401)
def forbidden_error(error):
    return make_response(render_template('show_error_text.html', title='Вы не авторизованы'), 403)


@app.errorhandler(403)
def forbidden_error(error):
    return make_response(render_template('show_error_text.html', title='Неправильный тип аккаунта'), 403)


@app.errorhandler(404)
def not_found(error):
    return make_response(render_template('show_error_text.html', title='Страница не найдена'), 404)


# User load
@login_manager.user_loader
def load_user(profile_id):
    prifile_id = int(profile_id)
    profile = get_session().query(ProfileType).get(profile_id)
    if not profile:
        return profile
    if profile.profile_type == 'User':
        return get_session().query(User).get(profile.account_id)
    if profile.profile_type == 'Restaurant':
        return get_session().query(Restaurant).get(profile.account_id)


# Main page
@app.route('/')
def main_page():
    return render_template('main_page.html', title='Order anywhere')


if __name__ == '__main__':
    app.register_blueprint(accounts.blueprint)
    app.register_blueprint(settings.blueprint)
    app.register_blueprint(organisations_settings.blueprint)
    app.register_blueprint(menus_settings.blueprint)
    app.register_blueprint(search.blueprint)
    app.register_blueprint(restaurant_settings.blueprint)
    app.register_blueprint(order.blueprint)

    port = int(os.environ.get('PORT', 3000))
    socketio.run(app, host='0.0.0.0', port=port)
