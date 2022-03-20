import os

import requests

from operations import abort_if_user

from flask import Blueprint, redirect, render_template, request, make_response, abort, url_for
from flask_login import login_required, login_user, logout_user, current_user

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

blueprint = Blueprint(
    'menus_settings',
    __name__,
    template_folder='templates'
)


# Categories change
@blueprint.route('/categories_add', methods=['GET', 'POST'])
@login_required
def categories_add():
    abort_if_user()
    form = CategoryForm()
    if form.validate_on_submit():
        if db_sess.query(Category).filter(Category.menu == current_user.menu, MenuItem.title == form.title.data).first():
            form.title.errors.append('Категория с таким именем уже существует')
            response = render_template('form.html', form=form, title='Создание категории')
            return response
        category = Category(
            title=form.title.data
        )
        menu = db_sess.query(Menu).get(current_user.menu_id)
        menu.categories.append(category)
        db_sess.commit()
        return redirect('/settings/menu')
    response = render_template('form.html', form=form, title='Создание категории')
    return response


@blueprint.route('/category_edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def category_edit(category_id):
    abort_if_user()
    category = db_sess.query(Category).filter(Category.menu == current_user.menu, Category.id == category_id).first()
    if not category:
        abort(404)
    form = CategoryForm()
    if form.validate_on_submit():
        if db_sess.query(Category).filter(Category.menu == current_user.menu, Category.title == form.title.data, Category.id != category.id).first():
            form.title.errors.append('Категория с таким именем уже существует')
            response = render_template('form.html', form=form, title='Изменение категории')
            return response
        category.title = form.title.data
        db_sess.commit()
        return redirect('/settings/menu')
    form.title.data = category.title
    response = render_template('form.html', form=form, title='Изменение категории')
    return response


@blueprint.route('/category_delete/<int:category_id>', methods=['GET', 'POST'])
@login_required
def category_delete(category_id):
    abort_if_user()
    category = db_sess.query(Category).filter(Category.menu == current_user.menu, Category.id == category_id).first()
    if not category:
        abort(404)
    if category.menu_items:
        response = redirect(url_for('settings.settings', current_setting='menu', error='В категории остались продукты'))
        return response
    form = SubmitForm()
    if form.validate_on_submit():
        db_sess.query(Category).filter(Category.id == category_id).delete()
        db_sess.commit()
        return redirect('/settings/menu')
    response = render_template('form.html', form=form, title='Подтверждение удаления', form_text=f'Вы уверены что хотите удалить категорию {category.title}')
    return response


@blueprint.route('/test', methods=['POST'])
def a():
    pass


# Menu change
@blueprint.route('/menu_items_add', methods=['GET', 'POST'])
@login_required
def menu_items_add():
    abort_if_user()
    form = MenuItemForm()
    if form.validate_on_submit():
        # Check to errors
        req_sess = requests.Session()
        data = req_sess.post(request.host_url + f'api/menu/{current_user.id}', data={
            'title': form.title.data,
            'price': form.price.data,
            'category': form.category.data
        }, files={
            'item_image': request.files['item_image']
        }, cookies=request.cookies.to_dict())
        if data.status_code != 200:
            abort(data.status_code)
        data = data.json()

        if not data['successfully']:
            for error in data['errors']:
                if error['error_field'] == 'title':
                    form.title.errors.append(error['error'])
                if error['error_field'] == 'category':
                    form.category.errors.append(error['error'])
            response = render_template('form.html', form=form, title='Создание продукта')
            return response
        if data['successfully']:
            return redirect('/settings/menu')
    response = render_template('form.html', form=form, title='Создание продукта')
    return response


@blueprint.route('/menu_item_edit/<int:menu_item_id>', methods=['GET', 'POST'])
@login_required
def menu_item_edit(menu_item_id):
    abort_if_user()
    menu_item = db_sess.query(MenuItem).filter(MenuItem.menu == current_user.menu, MenuItem.id == menu_item_id).first()
    if not menu_item:
        abort(404)
    form = MenuItemForm()
    if form.validate_on_submit():
        # Check to errors
        nice = True
        if db_sess.query(MenuItem).filter(MenuItem.menu == current_user.menu, MenuItem.title == form.title.data, MenuItem.id != menu_item_id).first():
            form.title.errors.append('Продукт с таким именем уже существует')
            nice = False
        if not db_sess.query(Category).filter(Category.menu == current_user.menu, Category.title == form.category.data).first():
            form.category.errors.append('Такой категории не существует')
            nice = False
        if not nice:
            response = render_template('form.html', form=form, title='Изменение продукта')
            return response

        if form.item_image.data:
            f = request.files['item_image']
            filename = f'menu_item_{menu_item.id}.jpg'
            menu_item.item_image = f.read()
        menu_item.title = form.title.data
        menu_item.price = form.price.data
        menu_item.category = db_sess.query(Category).filter(Category.menu == current_user.menu, Category.title == form.category.data).first()
        db_sess.commit()
        return redirect('/settings/menu')
    form.title.data = menu_item.title
    form.price.data = menu_item.price
    form.category.data = menu_item.category.title
    response = render_template('form.html', form=form, title='Изменение продукта')
    return response


@blueprint.route('/menu_item_delete/<int:menu_item_id>', methods=['GET', 'POST'])
@login_required
def menu_item_delete(menu_item_id):
    abort_if_user()
    menu_item = db_sess.query(MenuItem).filter(MenuItem.menu == current_user.menu, MenuItem.id == menu_item_id).first()
    if not menu_item:
        abort(404)
    form = SubmitForm()
    if form.validate_on_submit():
        db_sess.query(MenuItem).filter(MenuItem.id == menu_item_id).delete()
        db_sess.commit()
        return redirect('/settings/menu')
    response = render_template('form.html', form=form, title='Подтверждение удаления', form_text=f'Вы уверены что хотите удалить продукт {menu_item.title}')
    return response
