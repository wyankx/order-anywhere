import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Category(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'categories'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String)

    menu_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('menus.id'))
    menu = orm.relation('Menu')

    menu_items = orm.relation('MenuItem', back_populates='category', lazy='subquery')
