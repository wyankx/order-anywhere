import requests

from operations import abort_if_user

from flask import Blueprint, redirect, render_template, request, abort, url_for
from flask_login import login_required, current_user

from forms.menu_item import MenuItemForm
from forms.category import CategoryForm
from forms.submit import SubmitForm

from data.db_session import get_session

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
        data = requests.post(request.host_url + f'api/menu/{current_user.id}/categories', data={
            'title': form.title.data
        }, cookies=request.cookies.to_dict())
        if data.status_code != 200:
            abort(data.status_code)
        data = data.json()

        if not data['successfully']:
            for error in data['errors']:
                if error['error_field'] == 'title':
                    form.title.errors.append(error['error'])
            response = render_template('form.html', form=form, title='Создание категории')
            return response
        if data['successfully']:
            return redirect('/settings/menu')
    response = render_template('form.html', form=form, title='Создание категории')
    return response


@blueprint.route('/category_edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def category_edit(category_id):
    abort_if_user()
    category = get_session().query(Category).filter(Category.menu == current_user.menu, Category.id == category_id).first()
    if not category:
        abort(404)
    form = CategoryForm()
    if form.validate_on_submit():
        data = requests.put(request.host_url + f'api/menu/{current_user.id}/category/{category_id}', data={
            'title': form.title.data
        }, cookies=request.cookies.to_dict())
        if data.status_code != 200:
            abort(data.status_code)
        data = data.json()

        if not data['successfully']:
            for error in data['errors']:
                if error['error_field'] == 'title':
                    form.title.errors.append(error['error'])
            response = render_template('form.html', form=form, title='Изменение категории')
            return response
        if data['successfully']:
            return redirect('/settings/menu')
    form.title.data = category.title
    response = render_template('form.html', form=form, title='Изменение категории')
    return response


@blueprint.route('/category_delete/<int:category_id>', methods=['GET', 'POST'])
@login_required
def category_delete(category_id):
    abort_if_user()
    category = get_session().query(Category).filter(Category.menu == current_user.menu, Category.id == category_id).first()
    if not category:
        abort(404)
    if category.menu_items:
        response = redirect(url_for('settings.settings', current_setting='menu', error='В категории остались продукты'))
        return response
    form = SubmitForm()
    if form.validate_on_submit():
        data = requests.delete(request.host_url + f'api/menu/{current_user.id}/category/{category_id}', cookies=request.cookies.to_dict())
        if data.status_code != 200:
            abort(data.status_code)
        data = data.json()
        if data['successfully']:
            return redirect('/settings/menu')
    response = render_template('form.html', form=form, title='Подтверждение удаления', form_text=f'Вы уверены что хотите удалить категорию {category.title}')
    return response


# Menu change
@blueprint.route('/menu_items_add', methods=['GET', 'POST'])
@login_required
def menu_items_add():
    abort_if_user()
    form = MenuItemForm()
    if form.validate_on_submit():
        data = requests.post(request.host_url + f'api/menu/{current_user.id}', data={
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
    menu_item = requests.get(request.host_url + f'api/menu/{current_user.id}/item/{menu_item_id}')
    if menu_item.status_code != 200:
        abort(menu_item.status_code)
    menu_item = menu_item.json()
    form = MenuItemForm()
    if form.validate_on_submit():
        data = requests.put(request.host_url + f'api/menu/{current_user.id}/item/{menu_item_id}', data={
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
            response = render_template('form.html', form=form, title='Изменение продукта')
            return response
        if data['successfully']:
            return redirect('/settings/menu')
    form.title.data = menu_item['title']
    form.price.data = menu_item['price']
    form.category.data = menu_item['category']['title']
    response = render_template('form.html', form=form, title='Изменение продукта')
    return response


@blueprint.route('/menu_item_delete/<int:menu_item_id>', methods=['GET', 'POST'])
@login_required
def menu_item_delete(menu_item_id):
    abort_if_user()
    menu_item = requests.get(request.host_url + f'api/menu/{current_user.id}/item/{menu_item_id}')
    if menu_item.status_code != 200:
        abort(menu_item.status_code)
    menu_item = menu_item.json()
    form = SubmitForm()
    if form.validate_on_submit():
        response = requests.delete(request.host_url + f'api/menu/{current_user.id}/item/{menu_item_id}', cookies=request.cookies.to_dict())
        if response.status_code != 200:
            abort(response.status_code)
        response = response.json()
        if response['successfully']:
            return redirect('/settings/menu')
    response = render_template('form.html', form=form, title='Подтверждение удаления', form_text=f'Вы уверены что хотите удалить продукт {menu_item["title"]}')
    return response
