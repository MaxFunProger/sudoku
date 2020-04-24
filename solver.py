from random import randint


def initiate():
    box.append([0, 1, 2, 9, 10, 11, 18, 19, 20])
    box.append([3, 4, 5, 12, 13, 14, 21, 22, 23])
    box.append([6, 7, 8, 15, 16, 17, 24, 25, 26])
    box.append([27, 28, 29, 36, 37, 38, 45, 46, 47])
    box.append([30, 31, 32, 39, 40, 41, 48, 49, 50])
    box.append([33, 34, 35, 42, 43, 44, 51, 52, 53])
    box.append([54, 55, 56, 63, 64, 65, 72, 73, 74])
    box.append([57, 58, 59, 66, 67, 68, 75, 76, 77])
    box.append([60, 61, 62, 69, 70, 71, 78, 79, 80])
    for i in range(0, 81, 9):
        row.append(range(i, i + 9))
    for i in range(9):
        column.append(range(i, 80 + i, 9))


def valid(n, pos):
    current_row = pos // 9
    current_col = pos % 9
    current_box = (current_row // 3) * 3 + (current_col // 3)
    for i in row[current_row]:
        if grid[i] == n:
            return False
    for i in column[current_col]:
        if grid[i] == n:
            return False
    for i in box[current_box]:
        if grid[i] == n:
            return False
    return True


def solve():
    i = 0
    proceed = 1
    while i < 81:
        if given[i]:
            if proceed:
                i += 1
            else:
                i -= 1
        else:
            n = grid[i]
            prev = grid[i]
            while n < 9:
                if n < 9:
                    n += 1
                if valid(n, i):
                    grid[i] = n
                    proceed = 1
                    break
            if grid[i] == prev:
                grid[i] = 0
                proceed = 0
            if proceed:
                i += 1
            else:
                i -= 1


def easy_grid(board):
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            sch = 0
            for g in range(i, i + 3):
                for k in range(j, j + 3):
                    if board[g][k] != '.':
                        sch += 1
            flag = False
            m = randint(4, 5)
            while sch < m:
                for g in range(i, i + 3):
                    for k in range(j, j + 3):
                        if board[g][k] == '.' and randint(0, 1):
                            sch += 1
                            board[g][k] = res[g][k]
                            if sch == m:
                                flag = True
                                break
                    if flag:
                        break


def normal_grid(board):
    four = 0
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            sch = 0
            for g in range(i, i + 3):
                for k in range(j, j + 3):
                    if board[g][k] != '.':
                        sch += 1
            if sch == 4:
                four += 1
                break
            flag = False
            m = randint(3, 4)
            if four == 5:
                m = 3
            elif i == 6 and four < 4:
                m = 4
            if m == 4:
                four += 1
            while sch < m:
                for g in range(i, i + 3):
                    for k in range(j, j + 3):
                        if board[g][k] == '.' and randint(0, 1):
                            sch += 1
                            board[g][k] = res[g][k]
                            if sch == m:
                                flag = True
                                break
                    if flag:
                        break


easy = open('easy_pool.txt')
norm = open('normal_pool.txt')
hard = open('hard_pool.txt')
e_solve = open('easy_solve.txt', 'w')
n_solve = open('normal_solve.txt', 'w')
h_solve = open('hard_solve.txt', 'w')

for i in range(337):
    s = easy.readline().strip()
    grid = [0] * 81
    given = [False] * 81
    for j in range(81):
        if s[j] != '.':
            grid[j] = int(s[j])
            given[j] = True
    box = []
    row = []
    column = []
    initiate()
    solve()
    res = ''
    for j in range(81):
        res += str(grid[j])
    print(res, file=e_solve)
e_solve.close()
print('Easy finished!')
for i in range(337):
    s = norm.readline().strip()
    grid = [0] * 81
    given = [False] * 81
    for j in range(81):
        if s[j] != '.':
            grid[j] = int(s[j])
            given[j] = True
    box = []
    row = []
    column = []
    initiate()
    solve()
    res = ''
    for j in range(81):
        res += str(grid[j])
    print(res, file=n_solve)
n_solve.close()
print('Normal finished!')
for i in range(337):
    s = hard.readline().strip()
    grid = [0] * 81
    given = [False] * 81
    for j in range(81):
        if s[j] != '.':
            grid[j] = int(s[j])
            given[j] = True
    box = []
    row = []
    column = []
    initiate()
    solve()
    res = ''
    for j in range(81):
        res += str(grid[j])
    print(res, file=h_solve)
h_solve.close()
print('Hard finished!')
