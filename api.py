from flask import make_response, url_for, Flask, jsonify, redirect, request
from flask_login import login_required, login_user, logout_user, current_user

from flask_restful import reqparse, abort, Api, Resource
import werkzeug

from data.db_session import db_session as db_sess

from operations import abort_if_restaurant, abort_if_user

from data.models.menus import Menu
from data.models.users import User
from data.models.profile_types import ProfileType
from data.models.menu_items import MenuItem
from data.models.restaurants import Restaurant
from data.models.categories import Category
from data.models.orders import Order
from data.models.order_items import OrderItem

app = Flask(__name__)
api = Api(app)


# Images
@app.route('/menu_item_image/<int:menu_item_id>')
def menu_item_image(menu_item_id):
    image_binary = db_sess.query(MenuItem).get(menu_item_id).item_image
    if not image_binary:
        return redirect('/static/no_image/item.png')
    response = make_response(image_binary)
    response.headers.set('Content-Type', 'image/jpeg')
    return response


@app.route('/restaurant_image/<int:restaurant_id>')
def restaurant_image(restaurant_id):
    image_binary = db_sess.query(Restaurant).get(restaurant_id).profile_image
    if not image_binary:
        return redirect('/static/no_image/profile.png')
    response = make_response(image_binary)
    response.headers.set('Content-Type', 'image/jpeg')
    return response


# Menu
class MenuListResource(Resource):
    def get(self, restaurant_id):
        restaurant = db_sess.query(Restaurant).get(restaurant_id)
        if not restaurant:
            abort(404)
        print([category.to_dict(only=('id', 'title', 'menu_items.id', 'menu_items.title', 'menu_items.price')) for category in restaurant.menu.categories])
        print(restaurant.to_dict(only=('id', 'title')))
        response = jsonify({'categories': [category.to_dict(only=('id', 'title', 'menu_items.id', 'menu_items.title', 'menu_items.price')) for category in restaurant.menu.categories], 'restaurant': restaurant.to_dict(only=('id', 'title'))})
        return response

    @login_required
    def post(self, restaurant_id):
        abort_if_user()
        parser = reqparse.RequestParser()
        parser.add_argument('item_image', type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('title', required=True, type=str, location='values')
        parser.add_argument('price', required=True, type=int, location='values')
        parser.add_argument('category', required=True, type=str, location='values')
        print(request)
        args = parser.parse_args()

        # Check to errors
        nice = True
        errors = []
        if db_sess.query(MenuItem).filter(MenuItem.menu == current_user.menu, MenuItem.title == args['title']).first():
            errors.append({'error': 'Продукт с таким именем уже существует', 'error_field': 'title'})
            nice = False
        if not db_sess.query(Category).filter(Category.menu == current_user.menu, Category.title == args['category']).first():
            errors.append({'error': 'Такой категории не существует', 'error_field': 'category'})
            nice = False
        if not nice:
            response = jsonify({'successfully': False, 'errors': errors})
            return response
        menu = db_sess.query(Menu).get(current_user.menu_id)
        menu_item = MenuItem(
            title=args['title'],
            price=args['price'],
            category=db_sess.query(Category).filter(Category.menu == current_user.menu, Category.title == args['category']).first(),
            menu=menu
        )
        menu.items.append(menu_item)
        db_sess.commit()
        if args['item_image']:
            f = args['item_image']
            menu_item.item_image = f.read()
        db_sess.commit()
        return jsonify({'successfully': True})


class MenuResourse(Resource):
    def get(self, restaurant_id, menu_item_id):
        restaurant = db_sess.query(Restaurant).get(restaurant_id)
        if not restaurant:
            abort(404)
        menu_item = db_sess.query(MenuItem).filter(MenuItem.menu == restaurant_id, MenuItem.id == menu_item_id).first()
        if not menu_item:
            abort(404)
        response = jsonify(menu_item.to_dict(only=('title', 'price', 'category.title')) + {'item_image_url': f'/menu_item_image/{menu_item_id}'})
        return response

    def put(self, restaurant_id, menu_item_id):
        abort_if_user()
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True)
        parser.add_argument('price', required=True, type=int)
        parser.add_argument('category', required=True)
        args = parser.parse_args()

        if restaurant_id != current_user.id:
            abort(404)
        restaurant = db_sess.query(Restaurant).get(restaurant_id)
        if not restaurant:
            abort(404)
        menu_item = db_sess.query(MenuItem).filter(MenuItem.menu == restaurant_id, MenuItem.id == menu_item_id).first()
        if not menu_item:
            abort(404)

        nice = True
        errors = []
        if db_sess.query(MenuItem).filter(MenuItem.menu == current_user.menu, MenuItem.title == args['title'], MenuItem.id != menu_item_id).first():
            errors.append({'error': 'Продукт с таким именем уже существует', 'error_field': 'title'})
            nice = False
        if not db_sess.query(Category).filter(Category.menu == current_user.menu, Category.title == args['category']).first():
            errors.append({'error': 'Такой категории не существует', 'error_field': 'category'})
            nice = False
        if not nice:
            response = jsonify({'successfully': False, 'errors': errors})
            return response
        menu_item.title = args['title']
        menu_item.price = args['price']
        menu_item.category = db_sess.query(Category).filter(Category.menu == current_user.menu, Category.title == args['category']).first()
        if args['item_image'].data:
            f = request.files['item_image']
            menu_item.item_image = f.read()
        db_sess.commit()
        return jsonify({'successfully': True})

    def delete(self, restaurant_id, menu_item_id):
        abort_if_user()
        if restaurant_id != current_user.id:
            abort(404)
        restaurant = db_sess.query(Restaurant).get(restaurant_id)
        if not restaurant:
            abort(404)
        menu_item = db_sess.query(MenuItem).filter(MenuItem.menu == restaurant_id, MenuItem.id == menu_item_id).first()
        if not menu_item:
            abort(404)
        db_sess.query(MenuItem).filter(MenuItem.id == menu_item_id).delete()
        db_sess.commit()
        return jsonify({'successfully': True})


api.add_resource(MenuListResource, '/api/menu/<int:restaurant_id>')
api.add_resource(MenuResourse, '/api/menu/<int:restaurant_id>/<int:menu_item_id>')
