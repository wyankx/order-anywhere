from operations import abort_if_user

from flask import Blueprint, redirect, render_template, abort
from flask_login import login_required, current_user

from data import db_session

from forms.organisation import OrganisationForm
from forms.submit import SubmitForm

from data.models.restaurants import Restaurant
from data.models.restaurant_places import RestaurantPlace

blueprint = Blueprint(
    'organisations_settings',
    __name__,
    template_folder='templates'
)


# Organisations edit
@blueprint.route('/organisations_add', methods=['GET', 'POST'])
@login_required
def organisations_add():
    abort_if_user()
    form = OrganisationForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(RestaurantPlace).filter(RestaurantPlace.title == form.title.data, RestaurantPlace.restaurant == current_user).first():
            form.title.errors.append('Организация с таким названием уже существует')
            response = render_template('form.html', title='Создание организации', form=form)
            db_session.close_connection(db_sess)
            return response
        place = RestaurantPlace(
            title=form.title.data
        )
        restaurant = db_sess.query(Restaurant).get(current_user.id)
        restaurant.places.append(place)
        db_sess.commit()
        db_session.close_connection(db_sess)
        return redirect('/settings/organisations')
    return render_template('form.html', title='Создание организации', form=form)


@blueprint.route('/organisation_edit/<int:place_id>', methods=['GET', 'POST'])
@login_required
def organisation_edit(place_id):
    abort_if_user()
    db_sess = db_session.create_session()
    place = db_sess.query(RestaurantPlace).filter(RestaurantPlace.restaurant == current_user, RestaurantPlace.id == place_id).first()
    if not place:
        db_session.close_connection(db_sess)
        abort(404)
    form = OrganisationForm()
    if form.validate_on_submit():
        if db_sess.query(RestaurantPlace).filter(RestaurantPlace.title == form.title.data, RestaurantPlace.restaurant == current_user, RestaurantPlace.id != place_id).first():
            form.title.errors.append('Организация с таким названием уже существует')
            response = render_template('form.html', title='Изменение организации', form=form)
            db_session.close_connection(db_sess)
            return response
        place = db_sess.query(RestaurantPlace).filter(RestaurantPlace.restaurant == current_user, RestaurantPlace.id == place_id).first()
        place.title = form.title.data
        db_sess.commit()
        db_session.close_connection(db_sess)
        return redirect('/settings/organisations')
    form.title.data = place.title
    response = render_template('form.html', title='Изменение организации', form=form)
    db_session.close_connection(db_sess)
    return response


@blueprint.route('/organisation_delete/<int:place_id>', methods=['GET', 'POST'])
@login_required
def organisation_delete(place_id):
    abort_if_user()
    db_sess = db_session.create_session()
    place = db_sess.query(RestaurantPlace).filter(RestaurantPlace.restaurant == current_user, RestaurantPlace.id == place_id).first()
    if not place:
        db_session.create_session(db_sess)
        abort(404)
    form = SubmitForm()
    if form.validate_on_submit():
        db_sess.query(RestaurantPlace).filter(RestaurantPlace.id == place_id).delete()
        db_sess.commit()
        db_session.close_connection(db_sess)
        return redirect('/settings/organisations')
    response = render_template('form.html', form=form, title='Подтверждение удаления', form_text=f'Вы уверены что хотите удалить организацию {place.title}')
    db_session.close_connection(db_sess)
    return response
