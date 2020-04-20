import db_session
from grids_easy import *
from grids_normal import *
from grids_hard import *
from users import *


db_session.global_init('sudoku.sqlite')
session = db_session.create_session()

