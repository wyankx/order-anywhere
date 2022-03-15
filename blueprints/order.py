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
    'menus_settings',
    __name__,
    template_folder='templates'
)


@login_required
def get_order(restaurant_id):
    abort_if_restaurant()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter()
    order = db_sess.query(Order).filter(Order.user == user, Order.restaurant.id == restaurant_id).first()
    if not order:
        order = Order(
            price=0,
            restaurant_id=restaurant_id,
            user=user
        )
        db_sess.commit()
    return order
