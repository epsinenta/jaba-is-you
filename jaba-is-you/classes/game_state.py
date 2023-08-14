import enum


@enum.unique
class GameState(enum.Enum):
    """Перечисление изменений которые может сделать GameStrategy в GameContext"""
    STOP = enum.auto()  #: Остановить игру
    SWITCH = enum.auto()  #: Сменить стратегию
    BACK = enum.auto()  #: Вернуть прошлую стратегию
    FLIP = enum.auto()  #: Нарисовать на экране
