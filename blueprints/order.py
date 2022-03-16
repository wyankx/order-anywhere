import os

from operations import abort_if_restaurant

from flask import Blueprint, redirect, render_template, request, make_response, abort, url_for
from flask_login import login_required, login_user, logout_user, current_user

from forms.user_register import UserRegisterForm
from forms.restaurant_register import RestaurantRegisterForm
from forms.login import LoginForm
from forms.menu_item import MenuItemForm
from forms.category import CategoryForm
from forms.submit import SubmitForm

from data import db_session

from data.models.menus import Menu
from data.models.users import User
from data.models.profile_types import ProfileType
from data.models.menu_items import MenuItem
from data.models.restaurants import Restaurant
from data.models.categories import Category
from data.models.orders import Order

blueprint = Blueprint(
    'order',
    __name__,
    template_folder='templates'
)


@login_required
def get_order(restaurant_id):
    abort_if_restaurant()
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    restaurant = db_sess.query(Restaurant).get(restaurant_id)
    if not restaurant:
        abort(404)
    order = db_sess.query(Order).filter(Order.user == user, Order.restaurant == restaurant).first()
    if not order:
        order = Order(
            price=0,
            restaurant=restaurant,
            user=user
        )
        db_sess.add(order)
        db_sess.commit()
    db_sess.refresh(restaurant)
    return {'order': order, 'restaurant': restaurant, 'user': user}


@blueprint.route('/order/<int:restaurant_id>')
@login_required
def order(restaurant_id):
    abort_if_restaurant()
    order = get_order(restaurant_id)
    return render_template('order_page.html', order=order['order'], restaurant=order['restaurant'])
