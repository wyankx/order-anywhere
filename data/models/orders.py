import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Order(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    price = sqlalchemy.Column()
    is_finished = sqlalchemy.Column()

    restaurant_id = sqlalchemy.Column()
    restaurant = sqlalchemy.Column()

    user_id = sqlalchemy.Column()
    user = sqlalchemy.Column()

    order_items = sqlalchemy.Column()
