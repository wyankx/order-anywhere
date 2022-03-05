import datetime

import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    register_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    name = sqlalchemy.Column(sqlalchemy.String)
    surname = sqlalchemy.Column(sqlalchemy.String)

    login = sqlalchemy.Column(sqlalchemy.String, index=True)
    password = sqlalchemy.Column(sqlalchemy.String)

    orders = orm.relation('Order', back_populates='user')
