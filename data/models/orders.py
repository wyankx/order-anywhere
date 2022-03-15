import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Order(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    price = sqlalchemy.Column(sqlalchemy.Integer)
    state = sqlalchemy.Column(sqlalchemy.String, default='Is not sent')  # Is not sent/Awaiting payment/In progress

    restaurant_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('restaurants.id'))
    restaurant = orm.relation('Restaurant')

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = orm.relation('User')

    order_items = orm.relation('OrderItem', back_populates='order')
