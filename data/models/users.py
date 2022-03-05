import datetime

import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    register_date = sqlalchemy.Column()

    name = sqlalchemy.Column()
    surname = sqlalchemy.Column()

    login = sqlalchemy.Column()
    password = sqlalchemy.Column()

    orders = sqlalchemy.Column()
