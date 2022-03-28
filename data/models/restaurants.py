from werkzeug.security import generate_password_hash, check_password_hash

import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Restaurant(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'restaurants'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    profile_id = sqlalchemy.Column(sqlalchemy.Integer)
    profile_image = sqlalchemy.Column(sqlalchemy.LargeBinary)

    title = sqlalchemy.Column(sqlalchemy.String, index=True)

    login = sqlalchemy.Column(sqlalchemy.String, index=True)
    password = sqlalchemy.Column(sqlalchemy.String)

    redirect_after_send_order = sqlalchemy.Column(sqlalchemy.String)

    menu_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('menus.id'))
    menu = orm.relation('Menu')

    places = orm.relation('RestaurantPlace', back_populates='restaurant', lazy='subquery', cascade="all,delete", passive_deletes=True)
    orders = orm.relation('Order', back_populates='restaurant', lazy='subquery', cascade="all,delete", passive_deletes=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
