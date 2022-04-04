from operations import abort_if_user, abort_if_restaurant

from flask import Blueprint, redirect, render_template, request
from flask_login import login_required, current_user

from data.db_session import get_session
from data.models.profile_types import ProfileType
from data.models.restaurants import Restaurant
from data.models.users import User
from forms.restaurant_general_edit import RestaurantGeneralEditForm
from forms.submit import SubmitForm
from forms.user_general_edit import UserGeneralEditForm
from operations import abort_if_user, abort_if_restaurant

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
        if get_session().query(Restaurant).filter(Restaurant.title == form.title.data, Restaurant.id != current_user.id).first():
            form.title.errors.append('Ресторан с таким названием существует')
            response = render_template('form.html', title='Изменение ресторана', form=form)
            return response
        restaurant = get_session().query(Restaurant).get(current_user.id)
        restaurant.redirect_after_send_order = form.redirect_after_send_order.data
        restaurant.title = form.title.data
        if form.logo.data:
            f = request.files['logo']
            restaurant.profile_image = f.read()
        get_session().commit()
        return redirect('/settings/general')
    form.redirect_after_send_order.data = current_user.redirect_after_send_order
    form.title.data = current_user.title
    response = render_template('form.html', title='Изменение ресторана', form=form)
    return response


@blueprint.route('/restaurant_delete', methods=['GET', 'POST'])
@login_required
def restaurant_delete():
    abort_if_user()
    form = SubmitForm()
    if form.validate_on_submit():
        restaurant = get_session().query(Restaurant).filter(Restaurant.id == current_user.id).first()
        profile = get_session().query(ProfileType).filter(ProfileType.id == restaurant.profile_id).first()
        get_session().delete(restaurant)
        get_session().delete(profile)
        get_session().commit()
        return redirect('/')
    response = render_template('form.html', form=form, title='Подтверждение удаления', form_text=f'Вы уверены что хотите удалить аккаунт?')
    return response


# User edit
@blueprint.route('/user_edit', methods=['GET', 'POST'])
@login_required
def user_edit():
    abort_if_restaurant()
    form = UserGeneralEditForm()
    if form.validate_on_submit():
        user = get_session().query(User).get(current_user.id)
        user.name = form.name.data
        user.surname = form.surname.data
        get_session().commit()
        return redirect('/settings/general')
    form.name.data = current_user.name
    form.surname.data = current_user.surname
    response = render_template('form.html', title='Изменение пользователя', form=form)
    return response


@blueprint.route('/user_delete', methods=['GET', 'POST'])
@login_required
def user_delete():
    abort_if_restaurant()
    form = SubmitForm()
    if form.validate_on_submit():
        user = get_session().query(User).filter(User.id == current_user.id).first()
        profile = get_session().query(ProfileType).filter(ProfileType.id == user.profile_id).first()
        get_session().delete(user)
        get_session().delete(profile)
        get_session().commit()
        return redirect('/')
    response = render_template('form.html', form=form, title='Подтверждение удаления', form_text=f'Вы уверены что хотите удалить аккаунт?')
    return response
