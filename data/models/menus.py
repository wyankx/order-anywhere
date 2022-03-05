import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Menu(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'menus'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    restaurant_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('restaurants.id'))
    restaurant = orm.relation('Restaurant')

    items = orm.relation('MenuItem', back_populates='menu')