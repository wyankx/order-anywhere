from flask import abort
from flask_login import login_required, current_user
from flask_socketio import join_room
from data.db_session import get_session
from data.models.restaurant_places import RestaurantPlace
from operations import abort_if_user, abort_if_restaurant
from setup import socketio


@socketio.on('restaurant_place_connect')
@login_required
def socket_connect_restaurant_place(data):
    abort_if_user()
    restaurant_place_id = int(data['restaurant_place_id'])
    restaurant_place = get_session().query(RestaurantPlace).filter(RestaurantPlace.id == restaurant_place_id, RestaurantPlace.restaurant_id == current_user.id).first()
    if not restaurant_place:
        abort(404)
    join_room(f'restaurant_{str(restaurant_place_id)}')


@socketio.on('user_connect')
@login_required
def socket_connect_user():
    abort_if_restaurant()
    join_room(f'user_{str(current_user.id)}')
