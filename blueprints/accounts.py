from flask import Blueprint, redirect, render_template, request
from flask_login import login_required, login_user, logout_user

from forms.user_register import UserRegisterForm
from forms.restaurant_register import RestaurantRegisterForm
from forms.login import LoginForm

from data.db_session import db_session as db_sess

from data.models.menus import Menu
from data.models.users import User
from data.models.profile_types import ProfileType
from data.models.restaurants import Restaurant

blueprint = Blueprint(
    'accounts',
    __name__,
    template_folder='templates'
)


@blueprint.route('/user_register', methods=['GET', 'POST'])
def user_register():
    form = UserRegisterForm()
    additional_link = {
        'link': '/restaurant_register',
        'label': 'Регистрация для ресторана'
    }
    if form.validate_on_submit():
        nice = True
        if form.password.data != form.repeat_password.data:
            form.repeat_password.errors.append('Пароли не совпадают')
            nice = False
        if db_sess.query(User).filter(User.login == form.login.data).first():
            form.login.errors.append('Этот логин занят')
            nice = False
        if not nice:
            return render_template('form.html', title='Регистрация пользователя', form=form, additional_link=additional_link)

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


@blueprint.route('/restaurant_register', methods=['GET', 'POST'])
def restaurant_register():
    form = RestaurantRegisterForm()
    additional_link = {
        'link': '/user_register',
        'label': 'Регистрация для пользователя'
    }
    if form.validate_on_submit():
        nice = True
        if form.password.data != form.repeat_password.data:
            form.repeat_password.errors.append('Пароли не совпадают')
            nice = False
        if db_sess.query(Restaurant).filter(Restaurant.login == form.login.data).first():
            form.login.errors.append('Этот логин занят')
            nice = False
        if db_sess.query(Restaurant).filter(Restaurant.title == form.title.data).first():
            form.title.errors.append('Ресторан с таким названием существует')
            nice = False
        if not nice:
            response = render_template('form.html', title='Регистрация ресторана', form=form, additional_link=additional_link)
            return response

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
        if form.logo.data:
            f = request.files['logo']
            restaurant.profile_image = f.read()
        db_sess.commit()
        login_user(profile, remember=True)
        return redirect('/')
    return render_template('form.html', title='Регистрация ресторана', additional_link=additional_link, form=form)


# Login
@blueprint.route('/user_login', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    additional_link = {
        'link': '/restaurant_login',
        'label': 'Авторизация для ресторана'
    }
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            profile = db_sess.query(ProfileType).filter(ProfileType.id == user.profile_id).first()
            login_user(profile, remember=form.remember_me.data)
            return redirect("/")
        errors = ['Неправильный логин или пароль']
        response = render_template('form.html', title='Авторизация пользователя', form=form, additional_link=additional_link, errors=errors)
        return response
    return render_template('form.html', title='Авторизация пользователя', form=form, additional_link=additional_link)


@blueprint.route('/restaurant_login', methods=['GET', 'POST'])
def restaurant_login():
    form = LoginForm()
    additional_link = {
        'link': 'user_login',
        'label': 'Авторизация для пользователя'
    }
    if form.validate_on_submit():
        restaurant = db_sess.query(Restaurant).filter(Restaurant.login == form.login.data).first()
        if restaurant and restaurant.check_password(form.password.data):
            profile = db_sess.query(ProfileType).filter(ProfileType.id == restaurant.profile_id).first()
            login_user(profile, remember=form.remember_me.data)

            return redirect("/")

        return render_template('form.html', title='Авторизация ресторана', form=form, additional_link=additional_link, errors=['Неправильный логин или пароль'])
    return render_template('form.html', title='Авторизация ресторана', form=form, additional_link=additional_link)


# Logout
@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
