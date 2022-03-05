import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class MenuItem(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'menu_items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name = sqlalchemy.Column()
    price = sqlalchemy.Column()

    menu_id = sqlalchemy.Column()
    menu = sqlalchemy.Column()

    options = sqlalchemy.Column()
