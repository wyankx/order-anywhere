import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class RestaurantPlace(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'restaurant_places'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String)

    restaurant_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('restaurants.id'))
    restaurant = orm.relation('Restaurant')

    orders = orm.relation('Order', back_populates='restaurant_place', lazy='subquery', cascade="all,delete", passive_deletes=True)
