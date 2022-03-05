import datetime

import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Restaurant(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'restaurants'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    register_date = sqlalchemy.Column()

    title = sqlalchemy.Column()

    login = sqlalchemy.Column()
    password = sqlalchemy.Column()

    menu_id = sqlalchemy.Column()
    menu = sqlalchemy.Column()

    places = sqlalchemy.Column()
    orders = sqlalchemy.Column()
