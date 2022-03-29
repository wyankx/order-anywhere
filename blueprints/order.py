from operations import abort_if_restaurant, abort_if_user

from flask import Blueprint, redirect, render_template, request, abort
from flask_login import login_required, current_user

import requests

from data.db_session import get_session

from data.models.users import User
from data.models.menu_items import MenuItem
from data.models.restaurants import Restaurant
from data.models.orders import Order
from data.models.order_items import OrderItem
from data.models.restaurant_places import RestaurantPlace

blueprint = Blueprint(
    'order',
    __name__,
    template_folder='templates'
)


@login_required
def get_order(restaurant_id):
    abort_if_restaurant()
    user = get_session().query(User).get(current_user.id)
    restaurant = get_session().query(Restaurant).get(restaurant_id)
    if len(restaurant.places) == 0:
        return 'No places'
    if not restaurant:
        abort(404)
    order = get_session().query(Order).filter(Order.user == user, Order.restaurant == restaurant, Order.state == 'Is not sent').first()
    if not order:
        order = Order(
            price=0,
            restaurant=restaurant,
            user=user,
            restaurant_place_id=get_session().query(RestaurantPlace).filter(RestaurantPlace.restaurant_id == restaurant_id).first().id
        )
        get_session().add(order)
        get_session().commit()
    return requests.get(request.host_url + f'api/order/{order.id}', cookies=request.cookies).json()


def no_places():
    return render_template('show_error_text.html', title='Ресторан не создал организаций', additional_text='У ресторана нету организаций, следовательно нету места куда направить ваш заказ.')


@blueprint.route('/order/<int:restaurant_id>')
@login_required
def order(restaurant_id):
    abort_if_restaurant()
    order = get_order(restaurant_id)
    if order == 'No places':
        return no_places()
    menu = requests.get(request.host_url + f'api/menu/{restaurant_id}')
    if menu.status_code != 200:
        abort(menu.status_code)
    menu = menu.json()
    response = render_template('order_page.html', order=order, categories=menu['categories'], restaurant=menu['restaurant'], title='Заказ')
    return response


@blueprint.route('/order/<int:restaurant_id>/add_item/<int:menu_item_id>')
@login_required
def order_add_item(restaurant_id, menu_item_id):
    abort_if_restaurant()
    order = get_order(restaurant_id)
    if order == 'No places':
        return no_places()
    menu_item = get_session().query(MenuItem).filter(MenuItem.id == menu_item_id, MenuItem.menu_id == order['restaurant']['menu']['id']).first()
    if not menu_item:
        abort(404)
    try:
        order_item = OrderItem(
            count=int(request.args['count']),
            menu_item_id=menu_item.id,
            order_id=order['id']
        )
    except ValueError:
        abort(404)
    get_session().add(order_item)
    get_session().commit()
    update_order_price(restaurant_id)
    return redirect(f'/order/{restaurant_id}')


@blueprint.route('/order/<int:restaurant_id>/delete_item/<int:order_item_id>')
def order_delete_item(restaurant_id, order_item_id):
    abort_if_restaurant()
    order = get_order(restaurant_id)
    if order == 'No places':
        return no_places()
    api_response = requests.delete(request.host_url + f'api/order/{order["id"]}/{order_item_id}', cookies=request.cookies)
    if api_response.status_code != 200:
        abort(api_response.status_code)
    api_response = api_response.json()
    if api_response['successfully']:
        return redirect(f'/order/{restaurant_id}/show')


def update_order_price(restaurant_id):
    order = get_session().query(Order).get(get_order(restaurant_id)['id'])
    order.price = sum([item.menu_item.price * item.count for item in order.order_items])
    get_session().commit()


@blueprint.route('/order/<int:restaurant_id>/show')
@login_required
def order_show(restaurant_id):
    abort_if_restaurant()
    order = get_order(restaurant_id)
    if order == 'No places':
        return no_places()
    restaurant = get_session().query(Restaurant).get(restaurant_id)
    return render_template('order_show.html', order=order, restaurant=restaurant, title='Заказ', available_to_send=len(order['order_items']), error=request.args.get('error', None))


@blueprint.route('/order/restaurant_place_connect', methods=['POST'])
@login_required
def restaurant_place_connect():
    abort_if_user()
    restaurant_place_id = int(request.values['restaurant_place_id'])
    restaurant_place = get_session().query(RestaurantPlace).filter(RestaurantPlace.id == restaurant_place_id, RestaurantPlace.restaurant_id == current_user.id).first()
    if not restaurant_place:
        abort(404)
    return redirect(f'/order/restaurant_place_orders/{restaurant_place_id}')


@blueprint.route('/order/restaurant_place_orders/<int:restaurant_place_id>')
@login_required
def restaurant_place_orders(restaurant_place_id):
    restaurant_place = get_session().query(RestaurantPlace).filter(RestaurantPlace.id == restaurant_place_id, RestaurantPlace.restaurant_id == current_user.id).first()
    orders_in_progress = get_session().query(Order).filter(Order.restaurant_place_id == restaurant_place_id, Order.state == 'In progress').order_by(Order.id)
    orders_ready = get_session().query(Order).filter(Order.restaurant_place_id == restaurant_place_id, Order.state == 'Ready').order_by(Order.id)
    orders_awaiting_payment = get_session().query(Order).filter(Order.restaurant_place_id == restaurant_place_id, Order.state == 'Awaiting payment').order_by(Order.id)
    if not restaurant_place:
        abort(404)
    return render_template('restaurant_place_orders_show.html', restaurant_place=restaurant_place, orders_in_progress=orders_in_progress, orders_ready=orders_ready, orders_awaiting_payment=orders_awaiting_payment)


@blueprint.route('/order/<int:order_id>/set_state', methods=['POST'])
@login_required
def set_order_state(order_id):
    api_response = requests.post(request.host_url + f'api/order/{order_id}', data={'new_state': request.values['new_state']}, cookies=request.cookies.to_dict())
    if api_response.status_code != 200:
        abort(api_response.status_code)
    api_response = api_response.json()
    if api_response['successfully']:
        return redirect(request.values['back_redir_to'])


@blueprint.route('/orders_show')
@login_required
def orders_show():
    abort_if_restaurant()
    orders = get_session().query(Order).filter(Order.user_id == current_user.id, Order.state != 'Is not sent').order_by(Order.id)
    order_states_translate = {
        'Awaiting payment': 'Ожидает оплаты',
        'In progress': 'Готовится',
        'Ready': 'Готов',
        'Finished': 'Выдан'
    }
    return render_template('user_orders_show.html', orders=orders, order_states_translate=order_states_translate, title='Ваши заказы')
