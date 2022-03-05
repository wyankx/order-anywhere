import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Option(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'options'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name = sqlalchemy.Column()
    price = sqlalchemy.Column()

    item_id = sqlalchemy.Column()
    item = sqlalchemy.Column()
