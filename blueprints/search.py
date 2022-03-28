from operations import abort_if_restaurant

from flask import Blueprint, render_template, request
from flask_login import login_required

from data.db_session import get_session
from sqlalchemy.sql.expression import func

from data.models.restaurants import Restaurant

blueprint = Blueprint(
    'search',
    __name__,
    template_folder='templates'
)


@blueprint.route('/search')
@login_required
def search():
    abort_if_restaurant()
    response_list = get_session().query(Restaurant).filter(Restaurant.title.like(f'%{request.args["search"]}%')).order_by(func.length(Restaurant.title)).limit(5)
    response = render_template('search_response.html', response=list(response_list), title='Поиск ресторана')
    return response
