import datetime
import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase


class EasyGrid(SqlAlchemyBase):
    __tablename__ = 'easy_grids'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    grid = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    solution = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, default='')
    binary = sqlalchemy.Column(sqlalchemy.String, default='')

    def __repr__(self):
        return '<EasyGrid> {} {}>'.format(self.id, self.grid, self.solution)
