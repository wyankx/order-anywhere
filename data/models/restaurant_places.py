import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class RestaurantPlace(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'restaurant_places'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name = sqlalchemy.Column()
    latitude = sqlalchemy.Column()
    longitude = sqlalchemy.Column()

    restaurant_id = sqlalchemy.Column()
    restaurant = sqlalchemy.Column()
