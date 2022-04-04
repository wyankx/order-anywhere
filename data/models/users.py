from werkzeug.security import generate_password_hash, check_password_hash

import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    profile_id = sqlalchemy.Column(sqlalchemy.Integer)

    name = sqlalchemy.Column(sqlalchemy.String)
    surname = sqlalchemy.Column(sqlalchemy.String)

    login = sqlalchemy.Column(sqlalchemy.String, index=True)
    password = sqlalchemy.Column(sqlalchemy.String)

    orders = orm.relation('Order', back_populates='user', lazy='subquery', cascade="all,delete", passive_deletes=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
