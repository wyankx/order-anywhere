from setup import *

import os

from flask import render_template, make_response, redirect, abort
from flask_login import LoginManager, current_user

from data.models.menu_items import MenuItem

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

login_manager = LoginManager()
login_manager.init_app(app)

import api as api_file


@app.teardown_appcontext
def shutdown_session(exception=None):
    get_session().remove()


# Images
@app.route('/menu_item_image/<int:menu_item_id>')
def menu_item_image(menu_item_id):
    menu_item = get_session().query(MenuItem).get(menu_item_id)
    if not menu_item:
        abort(404)
    if not menu_item.item_image:
        return redirect('/static/no_image/item.png')
    response = make_response(menu_item.item_image)
    response.headers.set('Content-Type', 'image/jpeg')
    return response


@app.route('/restaurant_image/<int:restaurant_id>')
def restaurant_image(restaurant_id):
    restaurant = get_session().query(Restaurant).get(restaurant_id)
    if not restaurant:
        abort(404)
    if not restaurant.profile_image:
        return redirect('/static/no_image/profile.png')
    response = make_response(restaurant.profile_image)
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
