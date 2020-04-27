import db_session
from PIL import Image
from grids_easy import EasyGrid
from grids_normal import NormalGrid
from grids_hard import HardGrid
import cloudinary.uploader

d = {'а': 22, 'б': 45, 'в': 71, 'г': 99, 'д': 124, 'е': 150, 'ж': 178, 'з': 203, 'и': 230}
column = [175, 200, 225, 253, 281, 308, 337, 363, 390]
row = [22, 45, 70, 98, 123, 149, 177, 202, 229]

e = open('easy_pool.txt')
e_s = open('easy_solve.txt')
n = open('normal_pool.txt')
n_s = open('normal_solve.txt')
h = open('hard_pool.txt')
h_s = open('hard_solve.txt')
db_session.global_init('sudoku2.sqlite')
session = db_session.create_session()


def string_to_grid(s):
    res = []
    for i in range(9):
        res.append(s[i * 9:i * 9 + 9])
    return res


for i in range(337):
    s = n.readline().strip()
    s2 = n_s.readline().strip()
    grid = NormalGrid()
    grid.grid = s
    grid.solution = s2
    img = Image.open('test.png').convert('RGBA')
    s = string_to_grid(s)
    for j in range(9):
        for k in range(9):
            if s[j][k].isdigit():
                img2 = Image.open(f'digits/{s[j][k]}.png').convert('RGBA')
                img.paste(img2, (column[k], row[j]), img2)
                img.save('img_test.png')
    cloudinary.uploader.upload("img_test.png", public_id=f"normal_{i}", cloud_name='miximka', api_key='195543728586611',
                               api_secret='gHQC-LNvIgbVsW04HXvjlOBbPY4')
    grid.image = f'normal_{i}'
    session.add(grid)
    session.commit()
n.close()
n_s.close()
print('Normal completed!')

for i in range(337):
    s = h.readline().strip()
    s2 = h_s.readline().strip()
    grid = HardGrid()
    grid.grid = s
    grid.solution = s2
    img = Image.open('test.png').convert('RGBA')
    s = string_to_grid(s)
    for j in range(9):
        for k in range(9):
            if s[j][k].isdigit():
                img2 = Image.open(f'digits/{s[j][k]}.png').convert('RGBA')
                img.paste(img2, (column[k], row[j]), img2)
                img.save('img_test.png')
    cloudinary.uploader.upload("img_test.png", public_id=f"hard_{i}", cloud_name='miximka', api_key='195543728586611',
                               api_secret='gHQC-LNvIgbVsW04HXvjlOBbPY4')
    grid.image = f'hard_{i}'
    session.add(grid)
    session.commit()
h.close()
h_s.close()
print('Hard completed!')