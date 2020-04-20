# импортируем библиотеки
from flask import Flask, request
import logging
import db_session
import pymorphy2
from grids_easy import EasyGrid
from grids_normal import NormalGrid
from grids_hard import HardGrid
from users import User
from random import randint


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
used = []
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


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    db_session.global_init('sudoku.sqlite')
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
    global used, started, diff, diff2, difficulty, chosen, diff3, chosen_grid, chosen_grid_id, finished, new_game, diff4
    user_id = req['session']['user_id']
    session = db_session.create_session()
    users = session.query(User).filter(User.id == user_id).first()
    if users is None:
        check = 0
    else:
        check = users.chosen_grid
    if req['session']['new'] and not check:
        add_user = User()
        if session.query(User).filter(User.id == user_id).first() is None:
            add_user.id = user_id
            session.add(add_user)
            session.commit()
        if users:
            used = [users.easy_used, users.normal_used, users.hard_used]

        sessionStorage[user_id] = {
            'suggests': [
                "Начать",
                "Хватит",
                "Помощь",
                "Факт"
            ]
        }
        facts_user[user_id] = 0
        res['response']['text'] = 'Привет! Это игра Судоку. Скажи начать для продолжения,' \
                                  ' хватит для завершения. Скажи помощь для того, чтобы узнать правила игры или факт ' \
                                  'для получения рандомного факта.'
        res['response']['tts'] = 'Привет! Это игра Судоку. Скажи sil <[1000]> начать sil <[1000]> для продолжения,' \
                                  ' sil <[1000]> хватит sil <[1000]> для завершения. Скажи sil <[1000]> помощь' \
                                 ' sil <[1000]> для того,' \
                                 ' чтобы узнать правила игры или sil <[1000]> факт sil <[1000]> ' \
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

    if users.chosen_grid and not diff:
        chosen = True
        started = True
        chosen_grid = users.chosen_grid
        diff = True
        res['response']['tts'] = 'С возвращением! Продолжаем играть!'
        res['response']['text'] = ''
        for i in range(81):
            if i % 9 == 0 and i:
                res['response']['text'] = res['response']['text'] + '\n'
            res['response']['text'] = res['response']['text'] + chosen_grid[i]
        return

    if not started:
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

    if finished:
        if 'новая игра' in req['request']['original_utterance'].lower():
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

    if 'начать' in req['request']['original_utterance'].lower() or started or new_game:
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
                                             ' назови номер столбца , ' \
                                             'номер строки и нужную цифру от одного до девяти именно в таком порядке.'
                    '''res["card"]['type'] = 'BigImage'
                    res['card']['image_id'] = "image_id"
                    res['card']['title'] = 'Столбцы: 1, 2, 3, 4, 5, 6, 7, 8, 9\n' \
                                           'Строки: 1, 2, 3, 4, 5, 6, 7, 8, 9'''
                    chosen_grid, chosen_grid_id = choose_grid(difficulty, user_id)   # #########################
                    res['response']['text'] = ''
                    for i in range(81):
                        if i % 9 == 0 and i:
                            res['response']['text'] = res['response']['text'] + '\n'
                        res['response']['text'] = res['response']['text'] + chosen_grid[i]
                    return
            diff3 = False
            out = get_number(req['request']['original_utterance'].lower().split())
            out = out[:min(3, len(out))]
            if len(out) < 3:
                for i in req['request']['original_utterance'].lower().split():
                    if i.isdigit():
                        out.append(int(i))
            out = out[:min(3, len(out))]
            sch = 0
            for i in range(min(len(out), 3)):
                if out[i] < 1 or out[i] > 9:
                    sch -= 1
                else:
                    sch += 1
            if sch != 3:
                res['response']['tts'] = 'Неверный ход.'
                res['response']['text'] = 'Неверный ход.'
                return
            else:
                chosen_grid = string_to_grid(chosen_grid)
                if chosen_grid[out[1] - 1][out[0] - 1] != '.':
                    res['response']['tts'] = 'Неверный ход.'
                    res['response']['text'] = 'Неверный ход.'
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
                        res['response']['tts'] = 'Поздравляю, ты смог! Но никогда не мопешает' \
                                                  ' практиковаться больше, чтобы играть лучше!' \
                                                  ' Можешь сказать sil <[1000]> новая игра sil <[1000]> , чтобы ' \
                                                  'начать заново. Скажи sil <[1000]> хватит, чтобы завершить.'
                        res['response']['text'] = 'Поздравляю, ты смог!'
                        finished = True
                        return
                    else:
                        res['response']['text'] = ''
                        for i in range(81):
                            if i % 9 == 0 and i:
                                res['response']['text'] = res['response']['text'] + '\n'
                            res['response']['text'] = res['response']['text'] + chosen_grid[i]
                        return

        started = True
        if user_id not in facts_user.keys():
            facts_user[user_id] = 0
        session = db_session.create_session()
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
    elif 'помощь' in req['request']['original_utterance'].lower().split():
        if started:
            res['response']['text'] = 'Извини, но во время игры лучше не отвлекаться.'
            res['response']['tts'] = 'Извини, но во время игры лучше не отвлекаться.'
            return
        res['response']['text'] = 'Правила просты:\n' \
                                  '1) Заполни поле, используя только цифры от 1 до 9.\n' \
                                  '2) Заполни поле так, чтобы ни в строке, ни в столбце,' \
                                  ' ни в квадрате 3х3 не было одинаковых цифр.\n' \
                                  '3) Веселись, думай, разработай свою тактику!'
        res['response']['tts'] = 'Правила просты sil <[1000]> ' \
                                  'Первое sil <[500]> Заполни поле, используя только цифры от 1 до 9.' \
                                  'Второе sil <[500]> Заполни поле так, чтобы ни в строке, ни в столбце,' \
                                  ' ни в квадрате 3х3 не было одинаковых цифр.' \
                                  'Третье sil <[500]> Веселись, думай, разработай свою тактику!'
        if user_id not in facts_user.keys():
            facts_user[user_id] = 0
        del res['response']['buttons'][2]
        if get_fact(user_id) == "Извини, но у меня нет больше фактов.":
            del res['response']['buttons'][2]
    elif 'хватит' in req['request']['original_utterance'].lower().split():
        if chosen:
            session = db_session.create_session()
            users.chosen_grid = chosen_grid
            session.commit()
        res['response']['text'] = 'Уже уходишь. Ну ладно, до новых встреч.'
        res['response']['tts'] = 'Уже уходишь? Ну ладно, до новых встреч.'
        res['response']['end_session'] = True
        res['response']['buttons'] = []
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
        res['response']['end_session'] = False
    else:
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


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


def get_fact(user_id):
    if facts_user[user_id] < len(facts):
        facts_user[user_id] += 1
        return facts[facts_user[user_id] - 1]
    else:
        return "Извини, но у меня нет больше фактов."


def get_number(inp):
    p = ['первый', 'второй', 'третий', 'четвертый', 'пятый', 'шестой', 'седьмой', 'восьмой', 'девятый']
    out = []
    morhp = pymorphy2.MorphAnalyzer()
    for i in range(len(inp)):
        if morhp.parse(inp[i])[0].normal_form in p:
            out.append(p.index(inp[i]) + 1)
    return out


def choose_grid(dif, user_id):
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
        chosen_gr = session.query(EasyGrid).filter(EasyGrid.id == a).first().grid
        chosen_ind = session.query(EasyGrid).filter(EasyGrid.id == a).first().id
        return chosen_gr, chosen_ind
    elif dif == 1:
        user = session.query(User).filter(User.id == user_id).first()
        s = user.normal_used
        while a in s:
            a = randint(1, 337)
        s = s + ' ' + str(a)
        user.normal_used = s
        session.commit()
        chosen_gr = session.query(NormalGrid).filter(NormalGrid.id == a).first().grid
        chosen_ind = session.query(EasyGrid).filter(EasyGrid.id == a).first().id
        return chosen_gr, chosen_ind
    else:
        user = session.query(User).filter(User.id == user_id).first()
        s = user.hard_used
        while a in s:
            a = randint(1, 337)
        s = s + ' ' + str(a)
        user.hard_used = s
        session.commit()
        chosen_gr = session.query(HardGrid).filter(HardGrid.id == a).first().grid
        chosen_ind = session.query(EasyGrid).filter(EasyGrid.id == a).first().id
        return chosen_gr, chosen_ind


def string_to_grid(s):
    res = []
    for i in range(9):
        res.append(s[i * 9:i * 9 + 9])
    return res


def grid_to_string(s):
    res = ''
    for i in range(9):
        for j in range(9):
            res = res + str(s[i][j])
    return res


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
