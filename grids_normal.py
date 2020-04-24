import datetime
import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase


class NormalGrid(SqlAlchemyBase):
    __tablename__ = 'normal_grids'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    grid = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    solution = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return '<NormalGrid> {} {}>'.format(self.id, self.grid, self.solution)
