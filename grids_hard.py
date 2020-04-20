import datetime
import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase


class HardGrid(SqlAlchemyBase):
    __tablename__ = 'hard_grid'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    grid = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return '<HardGrid> {} {}>'.format(self.id, self.grid)
