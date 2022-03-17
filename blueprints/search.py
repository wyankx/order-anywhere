from operations import abort_if_restaurant

from flask import Blueprint, redirect, render_template, abort, request
from flask_login import login_required, current_user

from data import db_session
from sqlalchemy.sql.expression import func

from forms.organisation import OrganisationForm
from forms.submit import SubmitForm

from data.models.restaurants import Restaurant
from data.models.restaurant_places import RestaurantPlace

blueprint = Blueprint(
    'search',
    __name__,
    template_folder='templates'
)


@blueprint.route('/search')
@login_required
def search():
    abort_if_restaurant()
    db_sess = db_session.create_session()
    response_list = db_sess.query(Restaurant).filter(Restaurant.title.like(f'%{request.args["search"]}%')).order_by(func.length(Restaurant.title)).limit(5)
    response = render_template('search_response.html', response=list(response_list), title='Поиск ресторана')
    db_session.close_connection(db_sess)
    return response
