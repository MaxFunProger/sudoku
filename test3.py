import db_session
from PIL import Image
from base64 import b64decode, b64encode
from io import BytesIO
from grids_hard import HardGrid
from grids_normal import NormalGrid
from grids_easy import EasyGrid
from users import User
from urllib.request import urlopen

db_session.global_init('sudoku (5).sqlite')
session = db_session.create_session()

e = open('easy_code.txt', 'w')
n = open('normal_code.txt', 'w')
h = open('hard_code.txt', 'w')

for i in range(1, 338):
    code = session.query(EasyGrid).filter(EasyGrid.id == i).first().image
    print(code, file=e)
e.close()
print(1)
for i in range(1, 338):
    code = session.query(NormalGrid).filter(NormalGrid.id == i).first().image
    print(code, file=n)
n.close()
print(2)
for i in range(1, 338):
    code = session.query(HardGrid).filter(HardGrid.id == i).first().image
    print(code, file=h)
h.close()
print(3)
