import db_session
from grids_easy import EasyGrid
from grids_normal import NormalGrid
from grids_hard import HardGrid
from users import User
from django.core.validators import URLValidator
from django.core.validators import ValidationError
from YandexImages import YandexImages


yandex = YandexImages()
db_session.global_init('sudoku.sqlite')
