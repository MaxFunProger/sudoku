import db_session
from grids_easy import EasyGrid
from grids_normal import NormalGrid
from grids_hard import HardGrid
from users import User

db_session.global_init('sudoku.sqlite')
session = db_session.create_session()
for i in range(1, 338):
    u = session.query(EasyGrid).filter(EasyGrid.id == i).first()
    u.binary = ''
    session.commit()

for i in range(1, 338):
    u = session.query(NormalGrid).filter(NormalGrid.id == i).first()
    u.binary = ''
    session.commit()

for i in range(1, 338):
    u = session.query(HardGrid).filter(HardGrid.id == i).first()
    u.binary = ''
    session.commit()
