from flask import abort
from flask_login import login_required, current_user
from flask_socketio import join_room
from main import socketio
from data.db_session import get_session
from data.models.restaurant_places import RestaurantPlace
from operations import abort_if_user


@socketio.on('restaurant_place_connect')
@login_required
def socket_connect_restaurant_place(data):
    abort_if_user()
    restaurant_place_id = int(data['restaurant_place_id'])
    restaurant_place = get_session().query(RestaurantPlace).filter(RestaurantPlace.id == restaurant_place_id, RestaurantPlace.restaurant_id == current_user.id).first()
    if not restaurant_place:
        abort(404)
    join_room(str(restaurant_place_id))
