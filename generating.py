from random import randint, shuffle


class Board:
    def __init__(self):
        self.n = 3
        self.m = self.n**2
        self.table = [[((i * self.n + i // self.n + j) % (self.n * self.n) + 1)
                       for j in range(self.n * self.n)] for i in range(self.n * self.n)]
        print("The base table is ready!")

    def clear(self):
        self.table = [[((i * self.n + i // self.n + j) % (self.n * self.n) + 1)
                       for j in range(self.n * self.n)] for i in range(self.n * self.n)]
        print('Cleared!')

    def show(self):
        for i in range(self.n * self.n):
            print(self.table[i])

    def invert(self):
        for i in range(self.m):
            for j in range(i):
                self.table[i][j], self.table[j][i] = self.table[j][i], self.table[i][j]
        print('Inverted!')

    def swap_rows_small(self):
        for i in range(self.n):
            if randint(0, 1):
                a = 0
                b = 0
                while a == b:
                    a = randint(0, self.n - 1)
                    b = randint(0, self.n - 1)
                for j in range(self.m):
                    self.table[self.n * i + a][j], self.table[self.n * i + b][j] = self.table[self.n * i + b][j],\
                                                                                   self.table[self.n * i + a][j]
        print('row_small')

    def swap_columns_small(self):
        for i in range(self.n):
            if randint(0, 1):
                a = 0
                b = 0
                while a == b:
                    a = randint(0, self.n - 1)
                    b = randint(0, self.n - 1)
                for j in range(self.m):
                    self.table[j][self.n * i + a], self.table[j][self.n * i + b] = self.table[j][self.n * i + b],\
                                                                                   self.table[j][self.n * i + a]
        print('column_small')

    def swap_rows_big(self):
        a = 0
        b = 0
        while a == b:
            a = randint(0, self.n - 1)
            b = randint(0, self.n - 1)
        a, b = min(a, b), max(a, b)
        b = b - a
        for i in range(self.n * a, self.n * a + self.n):
            for j in range(self.m):
                self.table[i][j], self.table[i + self.n * b][j] = self.table[i + self.n * b][j], self.table[i][j]
        print('row_big')

    def swap_columns_big(self):
        a = 0
        b = 0
        while a == b:
            a = randint(0, self.n - 1)
            b = randint(0, self.n - 1)
        a, b = min(a, b), max(a, b)
        b = b - a
        for i in range(self.n * a, self.n * a + self.n):
            for j in range(self.m):
                self.table[j][i], self.table[j][i + self.n * b] = self.table[j][i + self.n * b], self.table[j][i]
        print('column_big')

    def mix(self, cnt=25):
        mixer = ['self.invert()', 'self.swap_rows_small()',
                 'self.swap_columns_small()', 'self.swap_rows_big()', 'self.swap_columns_big()']
        shuffle(mixer)
        sch = 0
        while sch < cnt:
            a = randint(0, 4)
            if randint(0, 1):
                eval(mixer[a])
                sch += 1
        print('Mixed!')


board = Board()
board.show()
board.mix()
print()
board.show()
