import os
import datetime

from flask import Flask, render_template, make_response, redirect
from flask_login import LoginManager, current_user
from flask_restful import Api

from data import db_session

# Will not work on Heroku, but needed for tests
from dotenv import load_dotenv

from data.models.menu_items import MenuItem

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

if __name__ == '__main__':
    db_session.global_init(os.environ.get('DATABASE_URL'))

from data.db_session import get_session

from blueprints import settings
from blueprints import accounts
from blueprints import organisations_settings
from blueprints import menus_settings
from blueprints import general_settings
from blueprints import search
from blueprints import order

from data.models.profile_types import ProfileType
from data.models.users import User
from data.models.restaurants import Restaurant
import views

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

login_manager = LoginManager()
login_manager.init_app(app)

import api as api_file


@app.teardown_appcontext
def shutdown_session(exception=None):
    get_session().remove()


# Images
@app.route('/menu_item_image/<int:menu_item_id>')
def menu_item_image(menu_item_id):
    image_binary = get_session().query(MenuItem).get(menu_item_id).item_image
    if not image_binary:
        return redirect('/static/no_image/item.png')
    response = make_response(image_binary)
    response.headers.set('Content-Type', 'image/jpeg')
    return response


@app.route('/restaurant_image/<int:restaurant_id>')
def restaurant_image(restaurant_id):
    image_binary = get_session().query(Restaurant).get(restaurant_id).profile_image
    if not image_binary:
        return redirect('/static/no_image/profile.png')
    response = make_response(image_binary)
    response.headers.set('Content-Type', 'image/jpeg')
    return response


# Error handlers
@app.errorhandler(401)
def unauthorized_error(error):
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
    if current_user.is_authenticated:
        if current_user.__class__.__name__ == 'Restaurant':
            return render_template('main_page.html', title='Order anywhere', restaurant=current_user)
    return render_template('main_page.html', title='Order anywhere')


if __name__ == '__main__':
    # Add API resources
    api.add_resource(api_file.MenuItemListResource, '/api/menu/<int:restaurant_id>')
    api.add_resource(api_file.MenuItemResource, '/api/menu/<int:restaurant_id>/item/<int:menu_item_id>')
    api.add_resource(api_file.MenuCategoryListResource, '/api/menu/<int:restaurant_id>/categories')
    api.add_resource(api_file.MenuCategoryResource, '/api/menu/<int:restaurant_id>/category/<int:category_id>')
    api.add_resource(api_file.OrderListResource, '/api/order/<int:order_id>')
    api.add_resource(api_file.OrderItemResource, '/api/order/<int:order_id>/<int:order_item_id>')

    # Register blueprints
    app.register_blueprint(accounts.blueprint)
    app.register_blueprint(settings.blueprint)
    app.register_blueprint(organisations_settings.blueprint)
    app.register_blueprint(menus_settings.blueprint)
    app.register_blueprint(search.blueprint)
    app.register_blueprint(general_settings.blueprint)
    app.register_blueprint(order.blueprint)

    port = int(os.environ.get('PORT', 3000))
    socketio.run(app, host='0.0.0.0', port=port, log_output=True)
