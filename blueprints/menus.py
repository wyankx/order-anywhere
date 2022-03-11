from operations import abort_if_user

from flask import Blueprint, redirect, render_template
from flask_login import login_required, login_user, logout_user, current_user

from forms.user_register import UserRegisterForm
from forms.restaurant_register import RestaurantRegisterForm
from forms.login import LoginForm
from forms.menu_item import MenuItemForm

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


@blueprint.route('/menu_items_add', methods=['GET', 'POST'])
@login_required
def menu_items_add():
    abort_if_user()
    db_sess = db_session.create_session()
    form = MenuItemForm()
    if form.validate_on_submit():
        if db_sess.query(MenuItem).filter(MenuItem.menu == current_user.menu, MenuItem.name == form.name).first():
            form.name.errors.append('Продукт с таким именем уже существует')
            return render_template('form.html', form=form, title='Создание продукта')
        menu_item = MenuItem(
            name=form.name.data,
            price=form.price.data,
            category=db_sess.query(Category).filter(Category.menu == current_user.menu).first(),
            menu=current_user.menu
        )
        db_sess.commit()
        if form.item_image:
            with open(f'menu_item_{menu_item.id}', 'wb') as file:
                file.write(form.item_image.data)
            menu_item.item_image = f'menu_item_{menu_item.id}'
        db_sess.commit()
        return redirect('/settings/menu')
    return render_template('form.html', form=form, title='Создание продукта')
