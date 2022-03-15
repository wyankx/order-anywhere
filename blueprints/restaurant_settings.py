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

from data import db_session

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


@blueprint.route('/restaurant_image/<int:restaurant_id>')
def menu_item_image(restaurant_id):
    db_sess = db_session.create_session()
    image_binary = db_sess.query(Restaurant).get(restaurant_id).profile_image
    if not image_binary:
        return redirect('/static/no_image/profile.png')
    response = make_response(image_binary)
    response.headers.set('Content-Type', 'image/jpeg')
    return response


# Restaurant edit
@blueprint.route('/restaurant_edit', methods=['GET', 'POST'])
@login_required
def restaurant_edit():
    abort_if_user()
    db_sess = db_session.create_session()
    form = RestaurantGeneralEditForm()
    if form.validate_on_submit():
        if db_sess.query(Restaurant).filter(Restaurant.title == form.title.data, Restaurant.id != current_user.id).first():
            form.title.errors.append('Ресторан с таким названием существует')
            return render_template('form.html', title='Изменение ресторана', form=form)
        restaurant = db_sess.query(Restaurant).get(current_user.id)
        restaurant.title = form.title.data
        if form.logo.data:
            f = request.files['logo']
            restaurant.profile_image = f.read()
        db_sess.commit()
        return redirect('/settings/general')
    return render_template('form.html', title='Изменение ресторана', form=form)
