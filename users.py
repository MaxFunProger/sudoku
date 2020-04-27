import datetime
import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    chosen_grid = sqlalchemy.Column(sqlalchemy.String, default='')
    easy_used = sqlalchemy.Column(sqlalchemy.String, default='')
    normal_used = sqlalchemy.Column(sqlalchemy.String, default='')
    hard_used = sqlalchemy.Column(sqlalchemy.String, default='')
    image = sqlalchemy.Column(sqlalchemy.String, default='')
    binary = sqlalchemy.Column(sqlalchemy.String, default='')
