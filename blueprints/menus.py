import os

from operations import abort_if_user

from flask import Blueprint, redirect, render_template, request, make_response
from flask_login import login_required, login_user, logout_user, current_user

from forms.user_register import UserRegisterForm
from forms.restaurant_register import RestaurantRegisterForm
from forms.login import LoginForm
from forms.menu_item import MenuItemForm
from forms.category import CategoryForm

from data import db_session

from data.models.menus import Menu
from data.models.users import User
from data.models.profile_types import ProfileType
from data.models.menu_items import MenuItem
from data.models.restaurants import Restaurant
from data.models.categories import Category

blueprint = Blueprint(
    'menus',
    __name__,
    template_folder='templates'
)


@blueprint.route('/menu_item_image/<int:menu_item_id>')
def menu_item_image(menu_item_id):
    db_sess = db_session.create_session()
    image_binary = db_sess.query(MenuItem).get(menu_item_id).item_image
    if not image_binary:
        return redirect('/static/no_image/item.png')
    response = make_response(image_binary)
    response.headers.set('Content-Type', 'image/jpeg')
    return response


# Categories
@blueprint.route('/categories_add', methods=['GET', 'POST'])
@login_required
def categories_add():
    abort_if_user()
    db_sess = db_session.create_session()
    form = CategoryForm()
    if form.validate_on_submit():
        if db_sess.query(Category).filter(Category.menu == current_user.menu, MenuItem.title == form.title.data).first():
            form.title.errors.append('Категория с таким именем уже существует')
            return render_template('form.html', form=form, title='Создание категории')
        category = Category(
            title=form.title.data
        )
        menu = db_sess.query(Menu).get(current_user.menu_id)
        menu.categories.append(category)
        db_sess.commit()
        return redirect('/settings/menu')
    return render_template('form.html', form=form, title='Создание категории')


# Menu change
@blueprint.route('/menu_items_add', methods=['GET', 'POST'])
@login_required
def menu_items_add():
    abort_if_user()
    db_sess = db_session.create_session()
    form = MenuItemForm()
    if form.validate_on_submit():
        if db_sess.query(MenuItem).filter(MenuItem.menu == current_user.menu, MenuItem.title == form.title.data).first():
            form.title.errors.append('Продукт с таким именем уже существует')
            return render_template('form.html', form=form, title='Создание продукта')
        menu = db_sess.query(Menu).get(current_user.menu_id)
        menu_item = MenuItem(
            title=form.title.data,
            price=form.price.data,
            category=db_sess.query(Category).filter(Category.menu == current_user.menu, Category.title == form.category.data).first(),
            menu=menu
        )
        menu.items.append(menu_item)
        db_sess.commit()
        if form.item_image.data:
            f = request.files['item_image']
            filename = f'menu_item_{menu_item.id}.jpg'
            menu_item.item_image = f.read()
        db_sess.commit()
        return redirect('/settings/menu')
    return render_template('form.html', form=form, title='Создание продукта')
