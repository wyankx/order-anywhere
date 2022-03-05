import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class OrderItem(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'order_items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    menu_item_id = sqlalchemy.Column()
    menu_item = sqlalchemy.Column()

    order_id = sqlalchemy.Column()
    order = sqlalchemy.Column()
