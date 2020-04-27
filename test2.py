import db_session
from PIL import Image
from base64 import b64decode, b64encode
from io import BytesIO
from grids_hard import HardGrid
from grids_normal import NormalGrid
from grids_easy import EasyGrid
from users import User
from urllib.request import urlopen

db_session.global_init('sudoku.sqlite')


def binary_pic(pic):
    with open(pic, 'rb') as f:
        return b64encode(f.read())


def export(binary):
    return BytesIO(b64decode(binary))


e_s = open('easy_solve.txt')
e = open('easy_pool.txt')
e_c = open('easy_code.txt')
e_b = open('easy_binary.txt')

n_s = open('normal_solve.txt')
n = open('normal_pool.txt')
n_c = open('normal_code.txt')
n_b = open('normal_binary.txt')

h_s = open('hard_solve.txt')
h = open('hard_pool.txt')
h_c = open('hard_code.txt')
h_b = open('hard_binary.txt')

session = db_session.create_session()

for i in range(337):
    s = e.readline().strip()
    s_s = e_s.readline().strip()
    s_c = e_c.readline().strip()
    s_b = e_b.readline().strip()
    grid = EasyGrid()
    grid.grid = s
    grid.solution = s_s
    grid.image = s_c
    grid.binary = s_b
    session.add(grid)
    session.commit()
e.close()
e_s.close()
e_b.close()
e_c.close()

for i in range(337):
    s = n.readline().strip()
    s_s = n_s.readline().strip()
    s_c = n_c.readline().strip()
    s_b = n_b.readline().strip()
    grid = NormalGrid()
    grid.grid = s
    grid.solution = s_s
    grid.image = s_c
    grid.binary = s_b
    session.add(grid)
    session.commit()
n.close()
n_s.close()
n_b.close()
n_c.close()

for i in range(337):
    s = h.readline().strip()
    s_s = h_s.readline().strip()
    s_c = h_c.readline().strip()
    s_b = h_b.readline().strip()
    grid = HardGrid()
    grid.grid = s
    grid.solution = s_s
    grid.image = s_c
    grid.binary = s_b
    session.add(grid)
    session.commit()
h.close()
h_s.close()
h_b.close()
h_c.close()
