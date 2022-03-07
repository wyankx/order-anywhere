import os
import datetime

from flask import Flask, render_template, redirect, abort
from flask_login import LoginManager, login_required, logout_user, current_user

from data import db_session

from forms.user_register import UserRegisterForm
from forms.restaurant_register import RestaurantRegisterForm

from data.models.users import User
from data.models.restaurants import Restaurant
from data.models.menus import Menu


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


def abort_if_restaurant():
    if current_user.__class__.__name__ == 'Restaurant':
        abort(403)


def abort_if_user():
    if current_user.__class__.__name__ == 'User':
        abort(403)


@app.errorhandler(403)
def forbidden_error():
    return render_template('bad_account_type.html')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/user_register', methods=['POST', 'GET'])
def user_register():
    form = UserRegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            form.repeat_password.errors.append('Пароли не совпадают')
            return render_template('user_register.html', title='Регистрация пользователя', form=form)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            form.login.errors.append('Этот логин занят')
            return render_template('user_register.html', title='Регистрация пользователя', form=form)
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            login=form.login.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
    return render_template('user_register.html', title='Регистрация пользователя', form=form)


@app.route('/restaurant_register', methods=['POST', 'GET'])
def restaurant_register():
    form = RestaurantRegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            form.repeat_password.errors.append('Пароли не совпадают')
            return render_template('restaurant_register.html', title='Регистрация ресторана', form=form)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            form.login.errors.append('Этот логин занят')
            return render_template('restaurant_register.html', title='Регистрация ресторана', form=form)
        restaurant = Restaurant(
            title=form.title.data,
            login=form.login.data
        )
        restaurant.set_password(form.password.data)
        menu = Menu()
        db_sess.add(menu)
        menu.restaurant.append(restaurant)
        db_sess.commit()
    return render_template('restaurant_register.html', title='Регистрация ресторана', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def main_page():
    return render_template('main_page.html', title='Order anywhere')


if __name__ == '__main__':
    db_session.global_init(os.environ.get('DATABASE_URL'))
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
