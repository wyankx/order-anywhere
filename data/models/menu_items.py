import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class MenuItem(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'menu_items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)

    menu_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('menus.id'))
    menu = orm.relation('Menu')
