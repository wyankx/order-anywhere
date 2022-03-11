import os
import datetime

from flask import Flask, render_template, redirect, abort, make_response
from flask_login import LoginManager, login_required, logout_user, current_user, login_user

from data import db_session

from forms.user_register import UserRegisterForm
from forms.restaurant_register import RestaurantRegisterForm
from forms.login import LoginForm
from forms.organisation import OrganisationForm

from data.models.profile_types import ProfileType
from data.models.users import User
from data.models.restaurants import Restaurant
from data.models.menus import Menu
from data.models.restaurant_places import RestaurantPlace


# Will not work on Heroku, but needed for tests
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
print(f' * SECRET_KEY: {os.environ.get("SECRET_KEY")}')
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

login_manager = LoginManager()
login_manager.init_app(app)


# Page for one profile type
def abort_if_restaurant():
    if current_user.__class__.__name__ == 'Restaurant':
        abort(403)


def abort_if_user():
    if current_user.__class__.__name__ == 'User':
        abort(403)


# Error handlers
@app.errorhandler(401)
def forbidden_error(error):
    return make_response(render_template('unauthorized.html', title='неправильный тип аккаунта'), 403)


@app.errorhandler(403)
def forbidden_error(error):
    return make_response(render_template('bad_account_type.html', title='неправильный тип аккаунта'), 403)


@app.errorhandler(404)
def not_found(error):
    return make_response(render_template('not_found.html', title='Страница не найдена'), 404)


# User load
@login_manager.user_loader
def load_user(profile_id):
    db_sess = db_session.create_session()
    profile = db_sess.query(ProfileType).get(profile_id)
    if not profile:
        return profile
    if profile.profile_type == 'User':
        return db_sess.query(User).get(profile.account_id)
    if profile.profile_type == 'Restaurant':
        return db_sess.query(Restaurant).get(profile.account_id)


# Register
@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    form = UserRegisterForm()
    additional_link = {
        'link': '/restaurant_register',
        'label': 'Регистрация для ресторана'
    }
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            form.repeat_password.errors.append('Пароли не совпадают')
            return render_template('user_register.html', title='Регистрация пользователя', form=form, additional_link=additional_link)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            form.login.errors.append('Этот логин занят')
            return render_template('user_register.html', title='Регистрация пользователя', form=form, additional_link=additional_link)
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            login=form.login.data
        )
        user.set_password(form.password.data)
        profile = ProfileType(
            profile_type=user.__class__.__name__,
        )
        db_sess.add(user)
        db_sess.add(profile)
        db_sess.commit()
        profile.account_id = user.id
        user.profile_id = profile.id
        db_sess.commit()
        login_user(profile, remember=True)
        return redirect('/')
    return render_template('form.html', title='Регистрация пользователя', form=form, additional_link=additional_link)


@app.route('/restaurant_register', methods=['GET', 'POST'])
def restaurant_register():
    form = RestaurantRegisterForm()
    additional_link = {
        'link': '/user_register',
        'label': 'Регистрация для пользователя'
    }
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            form.repeat_password.errors.append('Пароли не совпадают')
            return render_template('restaurant_register.html', title='Регистрация ресторана', form=form, additional_link=additional_link)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            form.login.errors.append('Этот логин занят')
            return render_template('restaurant_register.html', title='Регистрация ресторана', form=form, additional_link=additional_link)
        restaurant = Restaurant(
            title=form.title.data,
            login=form.login.data
        )
        restaurant.set_password(form.password.data)
        profile = ProfileType(
            profile_type=restaurant.__class__.__name__
        )
        menu = Menu()
        menu.restaurant.append(restaurant)
        db_sess.add(menu)
        db_sess.add(profile)
        db_sess.commit()
        profile.account_id = restaurant.id
        restaurant.profile_id = profile.id
        db_sess.commit()
        login_user(profile, remember=True)
        return redirect('/')
    return render_template('form.html', title='Регистрация ресторана', additional_link=additional_link, form=form)


# Login
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    additional_link = {
        'link': '/restaurant_login',
        'label': 'Авторизация для ресторана'
    }
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            profile = db_sess.query(ProfileType).filter(ProfileType.id == user.profile_id).first()
            login_user(profile, remember=form.remember_me.data)
            return redirect("/")
        errors = ['Неправильный логин или пароль']
        return render_template('form.html', title='Авторизация пользователя', form=form, additional_link=additional_link, errors=errors)
    return render_template('form.html', title='Авторизация пользователя', form=form, additional_link=additional_link)


@app.route('/restaurant_login', methods=['GET', 'POST'])
def restaurant_login():
    form = LoginForm()
    additional_link = {
        'link': 'user_login',
        'label': 'Авторизация для пользователя'
    }
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        restaurant = db_sess.query(Restaurant).filter(Restaurant.login == form.login.data).first()
        if restaurant and restaurant.check_password(form.password.data):
            profile = db_sess.query(ProfileType).filter(ProfileType.id == restaurant.profile_id).first()
            login_user(profile, remember=form.remember_me.data)
            return redirect("/")
        return render_template('form.html', title='Авторизация ресторана', form=form, additional_link=additional_link, errors=['Неправильный логин или пароль'])
    return render_template('form.html', title='Авторизация ресторана', form=form, additional_link=additional_link)


# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Main page
@app.route('/')
def main_page():
    return render_template('main_page.html', title='Order anywhere')


# Settings page
@app.route('/settings')
@login_required
def settings_redirect():
    if current_user.__class__.__name__ == 'Restaurant':
        return redirect('/settings/organisations')
    if current_user.__class__.__name__ == 'User':
        return redirect('/')


@app.route('/settings/<string:current_setting>')
@login_required
def settings(current_setting):
    if current_user.__class__.__name__ == 'Restaurant':
        # Settings dict which have next structure [setting -> html markup]
        setting_names = {'organisations': 'Организации', 'menu': 'Меню'}
        settings = {
            'organisations': [
                f'''<h1>Изменение организаций</h1>
                <a class="btn btn-outline-primary" href="/organisations_add">Добавить</a><br><br>
                {'<br>'.join([f'<div class="card" style="padding: 10px;">'
                              f'<div class="container-fluid d-flex" style="justify-content: space-between; align-items: center;">'
                              f'<div>'
                              f'<h3>{place.name}</h3>'
                              f'</div>'
                              f'<div class="d-flex" style="align-items: center;">'
                              f'<div style="margin: 0;">'
                              f'<p style="margin: 0;">'
                              f'<a class="btn btn-outline-primary" href="/organisation_edit/{place.id}">Изменить</a>'
                              f'<a class="btn btn-outline-danger" href="/organisation_delete/{place.id}">Удалить</a>'
                              f'</p>'
                              f'</div>'
                              f'</div>'
                              f'</div>'
                              f'</div>'
                              for place in current_user.places])}'''
            ],
            'menu': [
                f'''<h1>Изменение меню</h1>
                <a class="btn btn-outline-primary" href="/menu_items_add">Добавить</a><br><br>
                {'<br>'.join([f'<div class="card" style="padding: 10px;">'
                              f'<div class="container-fluid d-flex" style="justify-content: space-between; align-items: center;">'
                              f'<div>'
                              f'<h3>{menu_item.name}</h3>'
                              f'</div>'
                              f'<div class="d-flex" style="align-items: center;">'
                              f'<div style="margin: 0;">'
                              f'<p style="margin: 0;">'
                              f'<a class="btn btn-outline-primary" href="/menu_item_edit/{menu_item.id}">Изменить</a>'
                              f'<a class="btn btn-outline-danger" href="/menu_item_delete/{menu_item.id}">Удалить</a>'
                              f'</p>'
                              f'</div>'
                              f'</div>'
                              f'</div>'
                              f'<img src="/static/menu_item_images/{menu_item.item_image}">'
                              f'</div>'
                              for menu_item in current_user.menu.items])}'''
            ]
        }
    elif current_user.__class__.__name__ == 'User':
        # Settings dict which have next structure [setting -> html markup]
        setting_names = {}
        settings = {}
    if current_setting not in setting_names.keys():
        abort(404)
    return render_template('settings.html', title='Организации',  current_setting=current_setting, settings=settings, setting_names=setting_names)


# Organisations edit
@app.route('/organisations_add', methods=['GET', 'POST'])
@login_required
def organisations_add():
    abort_if_user()
    form = OrganisationForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(RestaurantPlace).filter(RestaurantPlace.name == form.name.data, RestaurantPlace.restaurant == current_user).first():
            form.name.errors.append('Организация с таким названием уже существует')
            return render_template('form.html', title='Создание организации', form=form)
        place = RestaurantPlace(
            name=form.name.data
        )
        restaurant = db_sess.query(Restaurant).get(current_user.id)
        restaurant.places.append(place)
        db_sess.commit()
        return redirect('/settings/organisations')
    return render_template('form.html', title='Создание организации', form=form)


@app.route('/organisation_edit/<int:place_id>', methods=['GET', 'POST'])
@login_required
def organisation_edit(place_id):
    abort_if_user()
    db_sess = db_session.create_session()
    if not db_sess.query(RestaurantPlace).filter(RestaurantPlace.restaurant == current_user, RestaurantPlace.id == place_id):
        abort(404)
    form = OrganisationForm()
    if form.validate_on_submit():
        if db_sess.query(RestaurantPlace).filter(RestaurantPlace.name == form.name.data, RestaurantPlace.restaurant == current_user).first():
            form.name.errors.append('Организация с таким названием уже существует')
            return render_template('form.html', title='Изменение организации', form=form)
        place = db_sess.query(RestaurantPlace).filter(RestaurantPlace.restaurant == current_user, RestaurantPlace.id == place_id).first()
        place.name = form.name.data
        db_sess.commit()
        return redirect('/settings/organisations')
    return render_template('form.html', title='Изменение организации', form=form)


@app.route('/organisation_delete/<int:place_id>')
@login_required
def organisation_delete(place_id):
    abort_if_user()
    db_sess = db_session.create_session()
    if not db_sess.query(RestaurantPlace).filter(RestaurantPlace.restaurant == current_user, RestaurantPlace.id == place_id):
        abort(404)
    db_sess.query(RestaurantPlace).filter(RestaurantPlace.restaurant == current_user, RestaurantPlace.id == place_id).delete()
    db_sess.commit()
    return redirect('/settings/organisations')


if __name__ == '__main__':
    db_session.global_init(os.environ.get('DATABASE_URL'))
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
