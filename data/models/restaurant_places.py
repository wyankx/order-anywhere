import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class RestaurantPlace(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'restaurant_places'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String)
    latitude = sqlalchemy.Column(sqlalchemy.Float)
    longitude = sqlalchemy.Column(sqlalchemy.Float)

    restaurant_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('restaurants.id'))
    restaurant = orm.relation('Restaurant')
