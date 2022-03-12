from operations import abort_if_user

from flask import Blueprint, redirect, render_template, abort
from flask_login import login_required, current_user

from data import db_session

from forms.organisation import OrganisationForm

from data.models.restaurants import Restaurant
from data.models.restaurant_places import RestaurantPlace

blueprint = Blueprint(
    'organisations',
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
            return render_template('form.html', title='Создание организации', form=form)
        place = RestaurantPlace(
            title=form.title.data
        )
        restaurant = db_sess.query(Restaurant).get(current_user.id)
        restaurant.places.append(place)
        db_sess.commit()
        return redirect('/settings/organisations')
    return render_template('form.html', title='Создание организации', form=form)


@blueprint.route('/organisation_edit/<int:place_id>', methods=['GET', 'POST'])
@login_required
def organisation_edit(place_id):
    abort_if_user()
    db_sess = db_session.create_session()
    place = db_sess.query(RestaurantPlace).filter(RestaurantPlace.restaurant == current_user, RestaurantPlace.id == place_id).first()
    if not place:
        abort(404)
    form = OrganisationForm()
    form.title.data = place.title
    if form.validate_on_submit():
        if db_sess.query(RestaurantPlace).filter(RestaurantPlace.title == form.title.data, RestaurantPlace.restaurant == current_user).first():
            form.title.errors.append('Организация с таким названием уже существует')
            return render_template('form.html', title='Изменение организации', form=form)
        place = db_sess.query(RestaurantPlace).filter(RestaurantPlace.restaurant == current_user, RestaurantPlace.id == place_id).first()
        place.title = form.title.data
        db_sess.commit()
        return redirect('/settings/organisations')
    return render_template('form.html', title='Изменение организации', form=form)


@blueprint.route('/organisation_delete/<int:place_id>')
@login_required
def organisation_delete(place_id):
    abort_if_user()
    db_sess = db_session.create_session()
    if not db_sess.query(RestaurantPlace).filter(RestaurantPlace.restaurant == current_user, RestaurantPlace.id == place_id):
        abort(404)
    db_sess.query(RestaurantPlace).filter(RestaurantPlace.restaurant == current_user, RestaurantPlace.id == place_id).delete()
    db_sess.commit()
    return redirect('/settings/organisations')
