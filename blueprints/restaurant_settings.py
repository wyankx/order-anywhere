import os

from operations import abort_if_user

from flask import Blueprint, redirect, render_template, request, make_response, abort, url_for
from flask_login import login_required, login_user, logout_user, current_user

from forms.user_register import UserRegisterForm
from forms.restaurant_register import RestaurantRegisterForm
from forms.login import LoginForm
from forms.menu_item import MenuItemForm
from forms.category import CategoryForm
from forms.submit import SubmitForm
from forms.restaurant_general_edit import RestaurantGeneralEditForm

from data.db_session import db_session as db_sess

from data.models.menus import Menu
from data.models.users import User
from data.models.profile_types import ProfileType
from data.models.menu_items import MenuItem
from data.models.restaurants import Restaurant
from data.models.categories import Category

blueprint = Blueprint(
    'restaurant_settings',
    __name__,
    template_folder='templates'
)


# Restaurant edit
@blueprint.route('/restaurant_edit', methods=['GET', 'POST'])
@login_required
def restaurant_edit():
    abort_if_user()
    form = RestaurantGeneralEditForm()
    if form.validate_on_submit():
        if db_sess.query(Restaurant).filter(Restaurant.title == form.title.data, Restaurant.id != current_user.id).first():
            form.title.errors.append('Ресторан с таким названием существует')
            response = render_template('form.html', title='Изменение ресторана', form=form)
            return response
        restaurant = db_sess.query(Restaurant).get(current_user.id)
        restaurant.title = form.title.data
        if form.logo.data:
            f = request.files['logo']
            restaurant.profile_image = f.read()
        db_sess.commit()
        return redirect('/settings/general')
    response = render_template('form.html', title='Изменение ресторана', form=form)
    return response