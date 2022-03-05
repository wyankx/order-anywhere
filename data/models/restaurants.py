import datetime

import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Restaurant(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'restaurants'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    register_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    title = sqlalchemy.Column(sqlalchemy.String)

    login = sqlalchemy.Column(sqlalchemy.String, index=True)
    password = sqlalchemy.Column(sqlalchemy.String)

    menu_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('menus.id'))
    menu = orm.relation('Menu', back_populates='restaurant')

    places = orm.relation('RestaurantPlace', back_populates='restaurant')
    orders = orm.relation('Order', back_populates='restaurant')
