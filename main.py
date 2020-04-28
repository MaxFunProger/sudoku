# импортируем библиотеки
from flask import Flask, request
import logging
import db_session
import os
import sys
from grids_easy import EasyGrid
from grids_normal import NormalGrid
from grids_hard import HardGrid
from users import User
from random import randint
from PIL import Image
from YandexImages import YandexImages
from urllib.request import urlopen
from requests import get



# библиотека, которая нам понадобится для работы с JSON
import json

# создаём приложение
# мы передаём __name__, в нем содержится информация,
# в каком модуле мы находимся.
# В данном случае там содержится '__main__',
# так как мы обращаемся к переменной из запущенного модуля.
# если бы такое обращение, например,
# произошло внутри модуля logging, то мы бы получили 'logging'
app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)
# Создадим словарь, чтобы для каждой сессии общения
# с навыком хранились подсказки, которые видел пользователь.
# Это поможет нам немного разнообразить подсказки ответов
# (buttons в JSON ответа).
# Когда новый пользователь напишет нашему навыку,
# то мы сохраним в этот словарь запись формата
# sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!" ]}
# Такая запись говорит, что мы показали пользователю эти три подсказки.
# Когда он откажется купить слона,
# то мы уберем одну подсказку. Как будто что-то меняется :)
sessionStorage = {}
facts_user = {}
facts = ['Бертхам Фельгенхауэр установил, что можно составить 6670903752021072936960 различных судоку!',
         'Ученые установили, что умственные упражнения, в том числе решение судоку,'
         ' способны сократить возраст мозга пожилых людей. Это приводит к улучшению памяти и'
         ' отсрочке спада интеллектуальной деятельности.',
         'Головоломки-судоку послужили причиной срыва судебного процесса в Сиднее, длящегося более двух месяцев.'
         ' Дело в том, что во время слушания дела несколько присяжных увлеченно решали судоку,'
         ' что подтвердил главный присяжный коллегии. Это и послужило поводом для прекращения процесса.',
         'Судоку не китайская и не японская головоломка. В современном виде она впервые была опубликована в США.',
         'Судоку стала хитом в 2005 году, она была признана самой быстрорастущей по популярности головоломкой.'
         ' Сравниться с ней может только кубик Рубика.',
         'Судоку может иметь только одно единственное решение. Преимущества нескольких решений'
         ' – это «сказка» владельцев некачественного генератора судоку.',
         'Первый всемирный чемпионат по судоку прошел в Италии в городе Лука в 2006 году.'
         ' Первым победителем стала Яна Тилова из Чехии.',
         'Решения судоку должны находиться логически, а не перебором или угадыванием!']
cats = ['213044/727f46a6589e927ea547', '1030494/0444ee843b32719ed9e1',
        '1030494/d5331e4641a4808ba8aa', '1652229/3ca647181ecc7547f1e7']
started = False
diff = False
old = ''
diff2 = False
difficulty = None
chosen = False
diff3 = False
chosen_grid = None
finished = False
chosen_grid_id = None
new_game = False
diff4 = False
solution = ''
delete = False
yandex = YandexImages()
# loaded = yandex.getLoadedImages()
# yandex.deleteImage(loaded['image']['id'])
yandex.set_auth_token('AgAAAAAqHEs_AAT7o7tmP0cMDkczmxBtEz1jnOM')


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    date_base_init()
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res):
    global started, diff, diff2, difficulty, chosen, diff3, chosen_grid, chosen_grid_id, finished,\
        new_game, diff4, solution, delete, old
    user_id = req['session']['user_id']
    session = db_session.create_session()
    users = session.query(User).filter(User.id == user_id).first()
    if users is None:
        check = 0
    else:
        check = 1
    if finished and check:
        users.image = ''
        users.chosen_grid = ''
        finished = False
        session.commit()
    if req['session']['new']:
        started = False
        diff = False
        diff2 = False
        difficulty = None
        chosen = False
        diff3 = False
        chosen_grid = None
        finished = False
        chosen_grid_id = None
        new_game = False
        diff4 = False
        delete = False
        solution = ''
    if not started and not new_game:
        res['response']['buttons'] = [
            {'title': 'Начать',
             'hide': True},
            {'title': 'Хватит',
             'hide': True},
            {'title': 'Помощь',
             'hide': True},
            {'title': 'Факт',
             'hide': True}
        ]
    else:
        res['response']['buttons'] = []
    if req['session']['new']:
        if not check:
            add_user = User()
            if session.query(User).filter(User.id == user_id).first() is None:
                add_user.id = user_id
                session.add(add_user)
                session.commit()
                users = session.query(User).filter(User.id == user_id).first()
        if not users.chosen_grid:
            sessionStorage[user_id] = {
                'suggests': [
                    "Начать",
                    "Хватит",
                    "Помощь",
                    "Факт"
                ]
            }
            facts_user[user_id] = 0
            res['response']['text'] = 'Привет! Это игра Судоку. Скажи <начать> для продолжения,' \
                                      ' <хватит> для завершения. Скажи <помощь> для того, чтобы узнать правила игры или <факт> ' \
                                      'для получения рандомного факта.'
            res['response']['tts'] = 'Привет! Это игра Судоку. Скажи sil <[500]> начать sil <[500]> для продолжения,' \
                                      ' sil <[500]> хватит sil <[500]> для завершения. Скажи sil <[500]> помощь' \
                                     ' sil <[500]> для того,' \
                                     ' чтобы узнать правила игры или sil <[500]> факт sil <[500]> ' \
                                      'для получения рандомного факта.'

            res['response']['buttons'] = [
                {'title': 'Начать',
                 'hide': True},
                {'title': 'Хватит',
                 'hide': True},
                {'title': 'Помощь',
                 'hide': True},
                {'title': 'Факт',
                 'hide': True}
                ]
            return
    elif 'хватит' in req['request']['original_utterance'].lower().split():
        if chosen:
            users.chosen_grid = chosen_grid
            session.commit()
        res['response']['text'] = 'Уже уходишь? Ну ладно, до новых встреч.'
        res['response']['tts'] = 'Уже уходишь? Ну ладно, до новых встреч.'
        res['response']['end_session'] = True
        res['response']['buttons'] = []
        return
    elif 'убери' in req['request']['original_utterance'].lower():
        started = False
        diff = False
        diff2 = False
        difficulty = None
        chosen = False
        diff3 = False
        chosen_grid = None
        finished = False
        chosen_grid_id = None
        new_game = False
        solution = ''
        delete = False
        users.chosen_grid = ''
        users.image = ''
        session.commit()
        res['response']['text'] = 'Хорошо, убрала. Что дальше?'
        res['response']['tts'] = 'Хорошо , убрала. Что дальше?'
        res['response']['buttons'] = [
                {'title': 'Начать',
                 'hide': True},
                {'title': 'Хватит',
                 'hide': True},
                {'title': 'Помощь',
                 'hide': True},
                {'title': 'Факт',
                 'hide': True}
                ]
        return
    elif 'помощь' in req['request']['original_utterance'].lower() or 'умеешь' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Правила просты:\n' \
                                  '1) Заполни поле, используя только цифры от 1 до 9.\n' \
                                  '2) Заполни поле так, чтобы ни в строке, ни в столбце,' \
                                  ' ни в квадрате 3х3 не было одинаковых цифр.\n' \
                                  '3) Для того, чтобы сделать ход, просто назови букву строки, номер столбца и цифру.' \
                                  ' Например: Е 5 9.\n' \
                                  '4) Скажи <начать> для запуска игры.\n' \
                                  '5) Скажи <новая игра>, чтобы начать заново новое поле.\n' \
                                  '6) Скажи <убери>, чтобы сбросить поле и перейти на главную.\n' \
                                  '7) Скажи <хватит> для выхода.\n' \
                                  '8) Веселись, думай, разработай свою тактику!'
        res['response']['tts'] = 'Правила просты sil <[1000]> ' \
                                  'Первое sil <[500]> Заполни поле, используя только цифры от 1 до 9.' \
                                  'Второе sil <[500]> Заполни поле так, чтобы ни в строке, ни в столбце,' \
                                  ' ни в квадрате 3х3 не было одинаковых цифр.' \
                                  'Третье sil <[500]> Для того, чтобы сделать ход, просто назови букву строки, номер столбца и цифру.' \
                                  'Четвёртое sil <[500]> Веселись, думай, разработай свою тактику!'
        if user_id not in facts_user.keys():
            facts_user[user_id] = 0
        if not started:
            res['response']['buttons'] = [
                    {'title': 'Начать',
                     'hide': True},
                    {'title': 'Хватит',
                     'hide': True},
                    {'title': 'Факт',
                     'hide': True}
                    ]
            if facts_user[user_id] >= len(facts):
                del res['response']['buttons'][2]
            return
        return
    elif 'факт' in req['request']['original_utterance'].lower().split():
        if started:
            res['response']['text'] = 'Не думаю, что во время игры стоит отвлекаться.'
            res['response']['tts'] = 'Не думаю , что во время игры стоит отвлекаться.'
            res['response']['end_session'] = False
            return
        res['response']['text'] = get_fact(user_id)
        res['response']['tts'] = res['response']['text']
        if res['response']['text'] == "Извини , но у меня нет больше фактов.":
            del res['response']['buttons'][3]
        else:
            res['response']['buttons'] = [
                {'title': 'Начать',
                 'hide': True},
                {'title': 'Хватит',
                 'hide': True},
                {'title': 'Помощь',
                 'hide': True},
                {'title': 'Факт',
                 'hide': True}
                ]
        res['response']['end_session'] = False
        return
    elif 'новая' in req['request']['original_utterance'].lower() and 'игра' in req['request']['original_utterance'].lower() or 'начать' in req['request']['original_utterance'].lower() and 'заново' in req['request']['original_utterance'].lower() or 'заново' in req['request']['original_utterance'].lower():
        started = False
        diff = False
        diff2 = False
        difficulty = None
        chosen = False
        diff3 = False
        chosen_grid = None
        finished = False
        chosen_grid_id = None
        new_game = True
        solution = ''
        delete = False
        users.chosen_grid = ''
        users.image = ''
        session.commit()
    if 'начать' in req['request']['original_utterance'].lower().split() and 'заново' not in req['request']['original_utterance'].lower().split() or started or new_game:
        new_game = False
        if started:
            if diff2:
                diff2 = False
                prev = False
                for i in req['request']['original_utterance'].lower().split():
                    if i == 'не':
                        prev = True
                        continue
                    else:
                        prev = False
                    if 'легкий' in i or 'лёгкий' in i:
                        if prev:
                            difficulty = 1
                        else:
                            difficulty = 0
                        break
                    elif 'нормальный' in i:
                        if prev:
                            difficulty = 2
                        else:
                            difficulty = 1
                        break
                    elif 'сложный' in i:
                        if prev:
                            difficulty = 1
                        else:
                            difficulty = 2
                        break
                if difficulty is None:
                    diff2 = True
                    res['response']['text'] = 'Не совсем поняла тебя. Повтори, пожалуйста!'
                    res['response']['tts'] = 'Не  совсем поняла тебя . Повтри , пожалуйста!'
                    res['response']['buttons'] = [
                        {'title': 'Легкий',
                         'hide': True},
                        {'title': 'Средний',
                         'hide': True},
                        {'title': 'Сложный',
                         'hide': True}
                    ]
                    return
                else:
                    diff3 = True
                    diff4 = True
            if diff3:
                if diff4:
                    diff4 = False
                    res['response']['tts'] = 'Начнем игру . Перед тобой исходное поле .' \
                                             ' Твоя цель - заполнить его цифрми от одного до девяти так ,' \
                                             ' чтобы в одной строке , одном столбце и в каждом квадрате' \
                                             ' три на три не было одинаковых цифр . Для совершения хода' \
                                             ' назови букву строки , ' \
                                             'номер столбца и нужную цифру от одного до девяти, именно в таком порядке.'
                    chosen_grid, chosen_grid_id, solution = choose_grid(difficulty, user_id)
                    users.chosen_grid = chosen_grid
                    session.commit()
                    a = start_condition_img(chosen_grid_id, difficulty, res)
                    users.image = a
                    session.commit()
                    res['response']['text'] = output_grid(chosen_grid)
                    return
            diff3 = False
            out = get_number(req['request']['original_utterance'].lower().split())
            if len(out) != 3:
                res['response']['text'] = 'Я тебя не понимаю! Повтори еще раз!'
                res['response']['tts'] = 'Я тебя не понимаю! Повтори еще раз!'
                return
            sch = 0
            for i in range(3):
                if out[i] < 1 or out[i] > 9:
                    sch -= 1
                else:
                    sch += 1
            if sch != 3:
                res['response']['tts'] = 'Неверный ход.'
                res['response']['text'] = 'Неверный ход.'
                return
            else:
                if type(solution) != str:
                    solution = grid_to_string(solution)
                if type(chosen_grid) != str:
                    chosen_grid = grid_to_string(chosen_grid)
                chosen_grid, solution = string_to_grid(chosen_grid, solution)
                if chosen_grid[out[1] - 1][out[0] - 1] != '.' or int(solution[out[1] - 1][out[0] - 1]) != int(out[2]):
                    res['response']['tts'] = 'Неверный ход, подумай ещё.'
                    res['response']['text'] = 'Неверный ход :('
                    return
                else:
                    chosen_grid[out[1] - 1] = chosen_grid[out[1] - 1][:out[0] - 1] + str(out[2]) + \
                                              chosen_grid[out[1] - 1][out[0]:]
                    chosen_grid = grid_to_string(chosen_grid)
                    users.chosen_grid = chosen_grid
                    session.commit()
                    if '.' not in chosen_grid:
                        chosen_grid = ''
                        session = db_session.create_session()
                        users.chosen_grid = ''
                        chosen = False
                        session.commit()
                        res['response']['tts'] = 'Поздравляю, ты смог! Но никогда не помешает' \
                                                  ' практиковаться больше, чтобы играть лучше!' \
                                                  ' Можешь сказать sil <[1000]> новая игра sil <[1000]> , чтобы ' \
                                                  'начать заново. Скажи sil <[1000]> хватит, чтобы завершить.'
                        res['response']['text'] = 'Поздравляю, мой друг, ты смог!'
                        res['response']['card'] = {}
                        res['response']['card']['type'] = 'BigImage'
                        res['response']['card']['image_id'] = cats[randint(0, 3)]
                        res['response']['card']['title'] = 'Поздравляю, мой друг, ты смог!'
                        res['response']['card']['description'] = 'Для начала новой игры скажи <новая игра>.'
                        started = False
                        diff = False
                        diff2 = False
                        difficulty = None
                        chosen = False
                        diff3 = False
                        chosen_grid = None
                        finished = True
                        chosen_grid_id = None
                        new_game = False
                        diff4 = False
                        solution = ''
                        delete = False
                        return
                    else:
                        res['response']['text'] = output_grid(chosen_grid)
                        if delete:
                            old = users.image
                        else:
                            delete = True
                        users.image = choose_box((out[0], out[1]), str(out[2]), res, users)
                        session.commit()
                        if old:
                            yandex.deleteImage(old)
                            old = ''
                        return
        started = True
        if user_id not in facts_user.keys():
            facts_user[user_id] = 0
        if not diff and started:
            diff = True
            diff2 = True
            res['response']['text'] = 'Выбери уровнь сложности'
            res['response']['tts'] = 'Выбери уровень сложности'
            res['response']['buttons'] = [
                {'title': 'Легкий',
                 'hide': True},
                {'title': 'Средний',
                 'hide': True},
                {'title': 'Сложный',
                 'hide': True}
            ]
            return

        if not started:
            del res['response']['buttons'][0]
            if get_fact(user_id) == "Извини, но у меня нет больше фактов.":
                del res['response']['buttons'][2]
    if users.chosen_grid and not diff:
        res['response']['buttons'] = []
        chosen = True
        started = True
        chosen_grid = users.chosen_grid
        solution = get_solve(difficulty, chosen_grid, user_id)
        diff = True
        res['response']['tts'] = 'С возвращением! Продолжаем играть!'
        res['response']['text'] = output_grid(chosen_grid)
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['image_id'] = users.image
        res['response']['card']['title'] = 'Строки: А, Б, В, Г, Д, Е, Ж, З, И\n' \
                                           'Столбцы: 1, 2, 3, 4, 5, 6, 7, 8, 9'
        return
    res['response']['text'] = 'Я не расслышала, что ты сказал! Повтори, пожалуйста!'
    res['response']['tts'] = 'Я не расслышала что ты сказал! Повтори пожалуйста!'
    res['response']['buttons'] = [
        {'title': 'Начать',
         'hide': True},
        {'title': 'Хватит',
         'hide': True},
        {'title': 'Помощь',
         'hide': True},
        {'title': 'Факт',
         'hide': True}
    ]
    return

def get_fact(user_id):
    if facts_user[user_id] < len(facts):
        facts_user[user_id] += 1
        return facts[facts_user[user_id] - 1]
    else:
        return "Извини, но у меня нет больше фактов."


def get_number(inp):
    out = []
    d = {'а': 0, 'б': 1, 'в': 2, 'г': 3, 'д': 4, 'е': 5, 'ж': 6, 'з': 7, 'и': 8}
    for i in range(len(inp)):
        if not len(out):
            if inp[i].isalpha():
                if len(inp[i]) == 1 and 'а' <= inp[i] <= 'и' and inp[i] != 'ё':
                    out.append(d[inp[i]])
                    continue
        if inp[i].isdigit() and len(out):
            out.append(int(inp[i]))
    if len(out) < 3:
        return [1]
    return [out[1], out[0] + 1, int(out[2])]



def choose_grid(dif, user_id):
    global solution
    session = db_session.create_session()
    a = str(randint(1, 337))
    if not dif:
        user = session.query(User).filter(User.id == user_id).first()
        s = user.easy_used
        while a in s:
            a = str(randint(1, 337))
        s = s + ' ' + a
        user.easy_used = s
        session.commit()
        a = int(a)
        solution = session.query(EasyGrid).filter(EasyGrid.id == a).first().solution
        chosen_gr = session.query(EasyGrid).filter(EasyGrid.id == a).first().grid
        chosen_ind = session.query(EasyGrid).filter(EasyGrid.id == a).first().id
        return chosen_gr, chosen_ind, solution
    elif dif == 1:
        user = session.query(User).filter(User.id == user_id).first()
        s = user.normal_used
        while a in s:
            a = randint(1, 337)
        s = s + ' ' + str(a)
        user.normal_used = s
        session.commit()
        a = int(a)
        solution = session.query(NormalGrid).filter(NormalGrid.id == a).fisrt().solution
        chosen_gr = session.query(NormalGrid).filter(NormalGrid.id == a).first().grid
        chosen_ind = session.query(EasyGrid).filter(EasyGrid.id == a).first().id
        return chosen_gr, chosen_ind, solution
    else:
        user = session.query(User).filter(User.id == user_id).first()
        s = user.hard_used
        while a in s:
            a = randint(1, 337)
        s = s + ' ' + str(a)
        user.hard_used = s
        session.commit()
        a = int(a)
        solution = session.query(HardGrid).filter(HardGrid.id == a).fisrt().solution
        chosen_gr = session.query(HardGrid).filter(HardGrid.id == a).first().grid
        chosen_ind = session.query(EasyGrid).filter(EasyGrid.id == a).first().id
        return chosen_gr, chosen_ind, solution


def string_to_grid(s, s2):
    res = []
    res2 = []
    for i in range(9):
        res.append(s[i * 9:i * 9 + 9])

    for i in range(9):
        res2.append(s2[i * 9:i * 9 + 9])
    return res, res2


def grid_to_string(s):
    res = ''
    for i in range(9):
        for j in range(9):
            res = res + str(s[i][j])
    return res


def output_grid(grid):
    grid = grid.replace('.', '_')
    p = ''
    sch = 0
    for i in range(19):
        if i % 2 == 0:
            p += '#' * 20 + '\n'
        else:
            p += '#'.join(grid[sch * 9:sch * 9 + 9]) + '\n'
            sch += 1
    return p


def date_base_init():
    app.config['SQLITE3_SETTINGS'] = {
    'host': 'sudoku.sqlite'
    }
    if __name__ != '__main__':
        app.root_path = os.path.dirname(os.path.abspath(__file__))
        if sys.platform != 'win32':
            app.config['SQLITE3_SETTINGS'] = {'host': '/home/Miximka/mysite/sudoku.sqlite'}
    db_session.global_init(app.config['SQLITE3_SETTINGS']['host'])


def choose_box(cords, parse, res, users):  # столбец строка
    global delete
    column = [175, 200, 225, 253, 281, 308, 337, 363, 390]
    row = [22, 45, 70, 98, 123, 149, 177, 202, 229]
    a = column[int(cords[0]) - 1]
    b = row[int(cords[1]) - 1]
    img1 = Image.open(urlopen(f'https://avatars.mds.yandex.net/get-dialogs-skill-card/{users.image}/orig')).convert('RGBA')
    img2 = Image.open(f'/home/Miximka/mysite/{parse}.png').convert('RGBA')
    img1.paste(img2, (a, b), img2)
    mas = ['img_test', 'test_1', 'test_2', 'test_3', 'test_4', 'test_5', 'test_6', 'test_7', 'test_8']
    k = mas[randint(0, 8)]
    img1.save(f'/home/Miximka/mysite/{k}.png')
    x = yandex.downloadImageFile(f'/home/Miximka/mysite/{k}.png')['id']
    res['response']['card'] = {}
    res['response']['card']['type'] = 'BigImage'
    res['response']['card']['image_id'] = x
    res['response']['card']['title'] = 'Строки:А, Б, В, Г, Д, Е, Ж, З, И\n' \
                                       'Столбцы:1, 2, 3, 4, 5, 6, 7, 8, 9'
    delete = True
    return x


def start_condition_img(id_, dif, rez):
    session = db_session.create_session()
    if dif == 0:
        img_id = session.query(EasyGrid).filter(EasyGrid.id == id_).first().image
    elif dif == 1:
        img_id = session.query(NormalGrid).filter(NormalGrid.id == id_).first().image
    else:
        img_id = session.query(HardGrid).filter(HardGrid.id == id_).first().image
    rez['response']['card'] = {}
    rez['response']['card']['type'] = 'BigImage'
    rez['response']['card']['image_id'] = img_id
    rez['response']['card']['title'] = 'Строки:А, Б, В, Г, Д, Е, Ж, З, И\n' \
                                       'Столбцы:1, 2, 3, 4, 5, 6, 7, 8, 9'
    return img_id


def get_solve(dif, chosen, user_id):
    session = db_session.create_session()
    used = int(session.query(User).filter(User.id == user_id).first().easy_used.split()[-1])
    if not dif:
        return session.query(EasyGrid).filter(EasyGrid.id == used).first().solution
    elif dif == 1:
        return session.query(NormalGrid).filter(NormalGrid.id == used).first().solution
    else:
        return session.query(HardGrid).filter(HardGrid.id == used).first().solution


def reload_image(plate):
    pass


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
