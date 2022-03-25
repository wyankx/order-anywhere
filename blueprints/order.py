import os

from operations import abort_if_restaurant

from flask import Blueprint, redirect, render_template, request, make_response, abort, url_for
from flask_login import login_required, login_user, logout_user, current_user

import requests

from forms.user_register import UserRegisterForm
from forms.restaurant_register import RestaurantRegisterForm
from forms.login import LoginForm
from forms.menu_item import MenuItemForm
from forms.category import CategoryForm
from forms.submit import SubmitForm

from data.db_session import db_session as db_sess

from data.models.menus import Menu
from data.models.users import User
from data.models.profile_types import ProfileType
from data.models.menu_items import MenuItem
from data.models.restaurants import Restaurant
from data.models.categories import Category
from data.models.orders import Order
from data.models.order_items import OrderItem
from data.models.restaurant_places import RestaurantPlace

blueprint = Blueprint(
    'order',
    __name__,
    template_folder='templates'
)


@login_required
def get_order(restaurant_id):
    abort_if_restaurant()
    user = db_sess.query(User).get(current_user.id)
    restaurant = db_sess.query(Restaurant).get(restaurant_id)
    if len(restaurant.places) == 0:
        return 'No places'
    if not restaurant:
        abort(404)
    order = db_sess.query(Order).filter(Order.user == user, Order.restaurant == restaurant).first()
    if not order:
        order = Order(
            price=0,
            restaurant=restaurant,
            user=user,
            restaurant_place_id=db_sess.query(RestaurantPlace).filter(RestaurantPlace.restaurant_id == restaurant_id).first().id
        )
        db_sess.add(order)
        db_sess.commit()
    return requests.get(request.host_url + f'api/order/{order.id}', cookies=request.cookies.to_dict()).json()


def no_places():
    return render_template('show_error_text.html', title='Ресторан не создал организаций', additional_text='У ресторана нету организаций, следовательно нету места куда направить ваш заказ.')


@blueprint.route('/order/<int:restaurant_id>')
@login_required
def order(restaurant_id):
    abort_if_restaurant()
    order = get_order(restaurant_id)
    if order == 'Not places':
        return no_places()
    menu = requests.get(request.host_url + f'api/menu/{restaurant_id}')
    if menu.status_code != 200:
        abort(menu.status_code)
    menu = menu.json()
    response = render_template('order_page.html', order=order, categories=menu['categories'], restaurant=menu['restaurant'], title='Заказ')
    return response


@blueprint.route('/order/<int:restaurant_id>/add_item/<int:menu_item_id>')
@login_required
def order_add_item(restaurant_id, menu_item_id):
    abort_if_restaurant()
    order = get_order(restaurant_id)
    if order == 'No places':
        return no_places()
    menu_item = db_sess.query(MenuItem).filter(MenuItem.id == menu_item_id, MenuItem.menu_id == order['restaurant']['menu']['id']).first()
    if not menu_item:
        abort(404)
    try:
        order_item = OrderItem(
            count=int(request.args['count']),
            menu_item_id=menu_item.id,
            order_id=order['id']
        )
    except ValueError:
        abort(404)
    db_sess.add(order_item)
    db_sess.commit()
    update_order_price(restaurant_id)
    return redirect(f'/order/{restaurant_id}')


def update_order_price(restaurant_id):
    order = db_sess.query(Order).get(get_order(restaurant_id)['id'])
    order.price = sum([item.menu_item.price * item.count for item in order.order_items])
    db_sess.commit()


@blueprint.route('/order/<int:restaurant_id>/show')
@login_required
def order_show(restaurant_id):
    abort_if_restaurant()
    order = get_order(restaurant_id)
    if order == 'No places':
        return no_places()
    restaurant = db_sess.query(Restaurant).get(restaurant_id)
    return render_template('order_show.html', order=order, restaurant=restaurant, title='Заказ')
