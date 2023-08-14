"""Модуль класса объекта"""
import os
import os.path
from copy import copy
from typing import List, Literal, Optional

import pygame

import settings
from classes.animation import Animation
from classes.palette import Palette
from classes.smooth_movement import SmoothMove
from elements.global_classes import sprite_manager, palette_manager
from global_types import SURFACE
from settings import DEBUG, TEXT_ONLY, SPRITE_ONLY, NOUNS, OPERATORS, PROPERTIES
from utils import get_pressed_direction

pygame.font.init()
font = pygame.font.Font("fonts/ConsolateElf.ttf", 15)


# TODO by quswadress
# Too many fields, refactor this please!

# Gospodin:
# Отнюдь. Слишком во многих файлах объекты и их поля
# вызываются без определения переменной как Object
# в циклых это вообще сделать, наверное, невозможно.
# Это значит, что
# Во первых, изменится половина кода
# Во вторых, придётся искать все упоминания объектов вручную
# В третьих, сами структуры выглядят по уродски, а иначе нужно
# Создавать классы, которые трудно сериализировать
# quswadress:
# #define MNE_LEN_REFAKTORIT "Это просто оправдание лени refactor-ть это."
# 1) Изменится половина кода? И что с того? MNE_LEN_REFACTORIT
# 2) MNE_LEN_REFACTORIT
# 3) Не спорю. Но если структуры могут работать с своими данными(то есть имеют какие-нибудь методы) то нет \
#       (именно поэтому есть параметр min-public-methods в pylint-е). Как пример можно привести структуру Palette.
# 4) Про часть с сериализацией, я не понял. А в чём собственно трудность? Если ты про /
#       большую связность классов друг с другом, то не думаю что это является серьёзной трудностью, просто /
#       сделай метод `serialize_this_shit` который будет принимать в себя все эти классы и возвращать байты, и всё.

class Object:
    """
    Объект правил, например, jaba, you, is, and, и т.д

    :ivar x: Позиция объекта на **сетке** уровня по оси х
    :ivar y: Позиция объекта на **сетке** уровня по оси y
    :ivar xpx: Абсцисса объекта на **экране** по оси х
    :ivar ypx: Ордината объекта на **экране** по оси y

    :ivar direction:
        Направление, в которое смотрит объект во время создания. Может принимать следующие значения:
        0 - Вверх
        1 - Вправо
        2 - Вниз
        3 - Влево
        Используется с правилами move, turn,
        shift и т.д.

    :ivar name: Название объекта
    :ivar is_text: Переменная определяющая является объект текстом, или нет

    :ivar width: Ширина спрайта
    :ivar height: Высота спрайта

    :ivar animation: Анимация объекта
    """

    def __init__(self, x: int, y: int, direction: int = 0, name: str = "empty",
                 is_text: bool = True, palette: Palette = palette_manager.get_palette("default"),
                 movement_state: int = 0, neighbours=None,
                 turning_side: Literal[0, 1, 2, 3, -1] = -1, animation=None,
                 safe=False, angle_3d: int = 90, is_3d=False, moved=False,
                 num_3d: int = 0, level_size=(32, 18), smooth_movement: Optional[SmoothMove] = None):

        self.status = ''
        self.name: str = name
        if self.name in TEXT_ONLY:
            self.is_text = True
        self.is_text = is_text

        self.turning_side = turning_side
        self.status_of_rotate: Literal[0, 1, 2, 3] = 0
        self.direction = direction
        self.direction_key_map = {
            0: 1,
            1: 0,
            2: 3,
            3: 2,
        }

        if neighbours is None:
            neighbours = []
        self.neighbours: List[List[Object]] = neighbours

        self._x = x
        self._y = y
        self._xpx = x * 50
        self._ypx = y * 50

        self.angle_3d = angle_3d
        self.num_3d = num_3d

        self.width = 50
        self.height = 50

        self.animation: Animation
        self.movement_state = movement_state
        self.animation = animation
        self.palette: Palette = palette

        self.is_hide = False
        self.is_hot = False
        self.is_power = False
        self.is_reverse = False
        self.is_safe = safe
        self.locked_sides = []
        self.is_open = False
        self.is_shut = False
        self.is_phantom = False
        self.is_still = False
        self.is_sleep = False
        self.is_weak = False
        self.is_float = False
        self.is_3d = is_3d
        self.level_processor = None
        self.is_fall = False
        self.is_word = False
        self.status_switch_name = 0
        self.has_objects = []

        self.moved = moved
        self.recursively_used = False

        self.level_size = level_size
        if self.name != 'empty' and self.animation is None:
            self.animation = self.animation_init()

        if smooth_movement is None:
            smooth_movement = SmoothMove(self.xpx, self.ypx, 0, 0, 1)
        self._movement: SmoothMove = smooth_movement

    @property
    def movement(self) -> SmoothMove:
        return self._movement

    def reset_movement(self):
        # TODO by quswadress: Add EmptySmoothMove instead of 0, 0, 1
        self._movement = SmoothMove(self.xpx, self.ypx, 0, 0, 1)

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int):
        self._x = value
        self._xpx = int(value * 50)

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int):
        self._y = value
        self._ypx = int(value * 50)

    @property
    def xpx(self) -> int:
        return self._xpx

    @xpx.setter
    def xpx(self, value: int):
        self._xpx = value
        self._x = int(value / 50)

    @property
    def ypx(self) -> int:
        return self._ypx

    @ypx.setter
    def ypx(self, value: int):
        self._ypx = value
        self._y = int(value / 50)

    def investigate_neighbours(self):
        """Исследует соседей объекта и возвращает правильный ключ к спрайту

        :return: Ключ для правильного выбора спрайтов и анимации
        :rtype: int
        """
        key_dict = {
            '': 0,
            'r': 1,
            'u': 2,
            'ur': 3,
            'l': 4,
            'rl': 5,
            'ul': 6,
            'url': 7,
            'b': 8,
            'rb': 9,
            'ub': 10,
            'urb': 11,
            'bl': 12,
            'rbl': 13,
            'ubl': 14,
            'urbl': 15
        }
        char_dict = ['u', 'r', 'b', 'l']
        key = ''
        for index, array in enumerate(self.neighbours):
            for level_object in array:
                if not level_object.is_text and level_object.name == self.name and \
                        char_dict[index] not in key:
                    key += char_dict[index]
        return key_dict[key]

    def animation_init(self) -> Animation:
        """Инициализирует анимацию объекта, основываясь на его имени,
           "Текстовом состоянии", направлении, стадии движения и т.д.
        """
        animation = Animation([], 200, (self.xpx, self.ypx))
        if (self.is_text or self.name in TEXT_ONLY) and self.name not in SPRITE_ONLY:
            path = os.path.join('./', 'sprites', 'text')
            animation.sprites = [pygame.transform.scale(sprite_manager.get(
                os.path.join(f"{path}", self.name, f"{self.name}_0_{index + 1}"), default=True, palette=self.palette),
                (50, 50)) for index in range(0, 3)]
        else:
            path = os.path.join('./', 'sprites', self.name)
            try:
                states = [int(name.split('_')[1]) for name in os.listdir(path) if os.path.isfile(
                    os.path.join(path, name))]
                state_max = max(states)
            except IndexError:
                print(
                    f'{self.name} fucked up while counting states -> probably filename is invalid')
                state_max = 0
            except FileNotFoundError:
                print(
                    f"{self.name} fucked up while searching for files. Probably folder is corrupt \
                    or does not exist. This shouldn't happen in any circumstances")
                state_max = 0

            if settings.DEBUG:
                print(self.__repr__(), end=" ")
                for k in sorted(self.__dict__.keys()):
                    if k.startswith('is_'):
                        print(k, self.__dict__[k], end=', ')
                print()

            try:
                if state_max == 0:
                    animation.sprites = [pygame.transform.scale(sprite_manager.get(
                        os.path.join(path,
                                     f'{self.name}_0_{index}'), default=True, palette=self.palette),
                        (50, 50)) for index in range(1, 4)]
                elif state_max == 15:
                    frame = self.investigate_neighbours()
                    animation.sprites = [pygame.transform.scale(sprite_manager.get(
                        os.path.join(path,
                                     f'{self.name}_{frame}_{index}'), default=True, palette=self.palette),
                        (50, 50)) for index in range(1, 4)]
                elif state_max == 3:
                    animation.sprites = [pygame.transform.scale(sprite_manager.get(
                        os.path.join(path,
                                     f'{self.name}_{self.movement_state % 4}_{index}'), default=True,
                        palette=self.palette),
                        (50, 50)) for index in range(1, 4)]
                elif state_max == 24:
                    animation.sprites = [pygame.transform.scale(sprite_manager.get(
                        os.path.join(path,
                                     f'{self.name}_{self.direction_key_map[self.direction] * 8}_{index}'), default=True,
                        palette=self.palette),
                        (50, 50)) for index in range(1, 4)]
                elif state_max == 27:
                    animation.sprites = [pygame.transform.scale(sprite_manager.get(
                        os.path.join(path,
                                     f'{self.name}_'
                                     f'{self.movement_state % 4 + self.direction_key_map[self.direction] * 8}_'
                                     f'{index}'), default=True, palette=self.palette),
                        (50, 50)) for index in range(1, 4)]
                elif state_max == 31:
                    keke_state = self.movement_state % 4 + max(self.direction_key_map[self.direction] * 8, 0) - int(
                        self.is_sleep
                    )
                    if keke_state < 0:
                        keke_state = 31
                    animation.sprites = [pygame.transform.scale(sprite_manager.get(
                        os.path.join(
                            path,
                            f'{self.name}_'
                            f'{keke_state}_'
                            f'{index}'), default=True, palette=self.palette),
                        (50, 50)) for index in range(1, 4)]
                elif DEBUG:
                    print(f'{self.name} somehow fucked up while setting animation')
            except FileNotFoundError:
                if self.movement_state == 0 and DEBUG:
                    print(f'{self.name} somehow fucked up while setting animation')
                else:
                    self.movement_state = 0
                    return self.animation_init()
        return animation

    def _draw_debug(self, screen: SURFACE, matrix: List[List[List["Object"]]]):
        """
        Подсвечивает объект цветами для дебага Кости.

        .. Циановый::
            Конец движения, то-есть куда объект двигается

        .. Пурпурный::
            Начало движения, то-есть откуда объект двигается

        .. Оранжевый::
            Положение объекта на матрице. Если он не находится на объекте - значит что-то пошло не так.
        """
        if not self.movement.done:
            surface = pygame.Surface((50, 50))
            surface.set_alpha(64)
            surface.fill("cyan")
            screen.blit(surface, (self.movement.start_x_pixel + self.movement.x_pixel_delta,
                                  self.movement.start_y_pixel + self.movement.y_pixel_delta),
                        special_flags=pygame.BLEND_RGBA_MULT)
            surface = pygame.Surface((40, 40))
            surface.set_alpha(64)
            surface.fill("magenta")
            screen.blit(surface, (
                self.movement.start_x_pixel + 5,
                self.movement.start_y_pixel + 5
            ), special_flags=pygame.BLEND_RGBA_ADD)
        y = x = None
        for y, line in enumerate(matrix):
            for x, cell in enumerate(line):
                for game_object in cell:
                    if game_object == self:
                        break
                else:
                    continue
                break
            else:
                continue
            break
        if y is not None and x is not None:
            surface = pygame.Surface((45, 45))
            surface.set_alpha(64)
            surface.fill("orange")
            screen.blit(surface, (x * 50 + 2, y * 50 + 2),
                        special_flags=pygame.BLEND_RGBA_ADD)

    def draw(self, screen: SURFACE, matrix: Optional[List[List[List["Object"]]]] = None):
        """
        Метод отрисовки объекта
        """
        if matrix is None:
            matrix = []
        new_x_and_y = self._movement.update_x_and_y()
        self.animation.position = self.xpx, self.ypx = new_x_and_y
        if not self.is_hide:
            self.animation.update()
            self.animation.draw(screen)
        if settings.DEBUG:
            self._draw_debug(screen, matrix)

    def unparse(self) -> str:
        """Сериализовать объект в строку"""
        return f'{self.x} {self.y} {self.direction} {self.name} {self.is_text}'

    def get_index(self, matrix) -> int:
        """Ищет индекс объекта в клетке матрицы для удаления
        (костыль от Vlastelin)

        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]
        :return: Индекс объекта в клетке массива
        :rtype: int
        """
        for i in range(len(matrix[self.y][self.x])):
            if matrix[self.y][self.x][i].name == self.name and self.text == matrix[self.y][self.x][i].text:
                return i
        return -1

    def move(self, matrix, level_rules, level_processor) -> None:
        """Выбор метода движения (2Д или 3Д)

        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]_
        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param level_processor: Объект класса игры, в котором
        движется объект
        :type level_processor: PlayLevel
        """
        if self.is_3d:
            self.move_3d(matrix, level_rules, level_processor)
        else:
            self.move_2d(matrix, level_rules, level_processor)

    def move_2d(self, matrix, level_rules, level_processor) -> None:
        """Метод движения объекта в 2Д

        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]
        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param level_processor: Объект класса игры, в котором
        движется объект
        :type level_processor: PlayLevel"""
        self.level_processor = level_processor

        if self.turning_side == 0:
            self.moved = self.motion(1, 0, matrix, level_rules)
            self.direction = 1
        elif self.turning_side == 1:
            self.moved = self.motion(0, -1, matrix, level_rules)
            self.direction = 0
        elif self.turning_side == 2:
            self.moved = self.motion(-1, 0, matrix, level_rules)
            self.direction = 3
        elif self.turning_side == 3:
            self.moved = self.motion(0, 1, matrix, level_rules)
            self.direction = 2

    def move_3d(self, matrix, level_rules, level_processor) -> None:
        """Метод движения объекта в 3Д

        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]
        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param level_processor: Объект класса игры, в котором
        движется объект
        :type level_processor: PlayLevel
        """
        self.level_processor = level_processor
        if self.turning_side == 2:
            matrix[self.y][self.x].pop(self.get_index(matrix))
            self.angle_3d = (self.angle_3d - 90) % 360
            matrix[self.y][self.x].append(copy(self))
        elif self.turning_side == 0:
            matrix[self.y][self.x].pop(self.get_index(matrix))
            self.angle_3d = (self.angle_3d + 90) % 360
            matrix[self.y][self.x].append(copy(self))
        elif self.turning_side == 1:
            if self.angle_3d == 0:
                self.direction = 1
                self.motion(1, 0, matrix, level_rules)
            if self.angle_3d in (180, -180):
                self.direction = 3
                self.motion(-1, 0, matrix, level_rules)
            if self.angle_3d in (90, -270):
                self.direction = 2
                self.motion(0, 1, matrix, level_rules)
            if self.angle_3d in (-90, 270):
                self.direction = 0
                self.motion(0, -1, matrix, level_rules)
        elif self.turning_side == 3:
            pass

    @staticmethod
    def find_side(delta_x, delta_y) -> Optional[str]:
        """Поиск направления движения

        :param delta_x: Сдвиг объекта по оси x
        :type delta_x: int
        :param delta_y: Сдвиг объекта по оси y
        :type delta_y: int
        :return: Сторона движения
        """
        side = None
        if delta_y > 0:
            side = 'down'
        elif delta_y < 0:
            side = 'up'
        if delta_x > 0:
            side = 'right'
        elif delta_x < 0:
            side = 'left'
        return side

    def update_parameters(self, delta_x, delta_y, matrix):
        """Обновление параметров объекта

        :param delta_x: Сдвиг объекта по оси x
        :type delta_x: int
        :param delta_y: Сдвиг объекта по оси y
        :type delta_y: int
        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]
        """
        self._movement.start_x_pixel = self._xpx
        self._movement.start_y_pixel = self._ypx
        if not self.is_still:
            self.x += delta_x
            self.y += delta_y
        self.animation = None
        self.movement_state += 1
        self.moved = True
        side = self.find_side(delta_x, delta_y)
        if side == 'down':
            self.status_of_rotate = 3
            self.direction = 2
        elif side == 'up':
            self.status_of_rotate = 1
            self.direction = 0
        elif side == 'right':
            self.status_of_rotate = 0
            self.direction = 1
        elif side == 'left':
            self.status_of_rotate = 2
            self.direction = 3
        matrix[self.y][self.x].append(copy(self))
        self._movement.x_pixel_delta = self._xpx - self._movement.start_x_pixel
        self._movement.y_pixel_delta = self._ypx - self._movement.start_y_pixel
        self._movement.rerun(0.05)

    def check_swap(self, delta_x, delta_y, matrix, level_rules, rule_object) -> bool:
        """Проверяет правило swap у объекта и сразу
        выполняет действие, если возможно

        :param delta_x: Сдвиг объекта по оси x
        :type delta_x: int
        :param delta_y: Сдвиг объекта по оси y
        :type delta_y: int
        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]
        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param rule_object: Объект, с которым движущийся объект
        потенциально может свапаться
        :type rule_object: Object
        :return: неизвестную фигню
        :rtype: bool
        """
        for rule in level_rules:
            if ((not rule_object.is_text and f'{rule_object.name} is swap' in rule.text_rule)
                    or (f'{self.name} is swap' in rule.text_rule and not self.is_phantom) or
                    (f'text is swap' in rule.text_rule and (rule_object.name in TEXT_ONLY
                                                            or rule_object.is_text))
                    or (f'text is swap' in rule.text_rule and (self.name in TEXT_ONLY
                                                               or self.is_text)))\
                    and rule.check_fix(self, matrix, level_rules):
                matrix[self.y][self.x].pop(self.get_index(matrix))
                self.update_parameters(delta_x, delta_y, matrix)
                matrix[self.y][self.x].pop(rule_object.get_index(matrix))
                rule_object.update_parameters(-delta_x, -delta_y, matrix)
                return True
        return False

    def check_melt(self, delta_x, delta_y, matrix, level_rules, rule_object) -> bool:
        """Проверяет правило melt у объекта и сразу
        выполняет действие, если возможно

        :param delta_x: Сдвиг объекта по оси x
        :type delta_x: int
        :param delta_y: Сдвиг объекта по оси y
        :type delta_y: int
        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]
        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param rule_object: Объект, с которым движущийся объект
        потенциально может взаимодействовать
        :type rule_object: Object
        :return: True если объект выжил иначе False
        :rtype: bool
        """
        if self.can_interact(rule_object, level_rules):
            if not self.object_can_stop(rule_object, level_rules, matrix, True):
                if not self.is_safe:
                    for rule in level_rules:
                        if ((f'{self.name} is melt' in rule.text_rule and not self.is_text)
                                or (f'text is melt' in rule.text_rule and (self.name in TEXT_ONLY
                                                                           or self.name in NOUNS and self.is_text)))\
                                and rule.check_fix(self, matrix, level_rules):
                            for sec_rule in level_rules:
                                if not rule_object.is_text and f'{rule_object.name} is hot' in sec_rule.text_rule\
                                        and sec_rule.check_fix(rule_object, matrix, level_rules):
                                    matrix[self.y][self.x].pop(
                                        self.get_index(matrix))
                                    return False
                for rule in level_rules:
                    if self.is_hot and ((not rule_object.is_text and f'{rule_object.name} is melt' in rule.text_rule) or
                                        (f'text is melt' in rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                                or rule_object.is_text)))\
                            and rule.check_fix(rule_object, matrix, level_rules):
                        matrix[self.y + delta_y][self.x +
                                                 delta_x].pop(rule_object.get_index(matrix))
            return True

    def check_weak(self, delta_x, delta_y, matrix, level_rules, rule_object) -> bool:
        """Проверяет правило weak у объекта и сразу
        выполняет действие, если возможно

        :param delta_x: Сдвиг объекта по оси x
        :type delta_x: int
        :param delta_y: Сдвиг объекта по оси y
        :type delta_y: int
        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]
        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param rule_object: Объект, с которым движущийся объект
        потенциально может взаимодействовать
        :type rule_object: Object
        :return: True если объект выжил иначе False
        :rtype: bool
        """
        if self.can_interact(rule_object, level_rules):
            if not self.is_safe:
                for rule in level_rules:
                    if ((f'{rule_object.name} is stop' in rule.text_rule and not rule_object.is_text)
                        or (f'text is stop' in rule.text_rule and (rule_object.name in TEXT_ONLY or rule_object.is_text)))\
                            and self.is_weak \
                            and rule.check_fix(rule_object, matrix, level_rules):
                        matrix[self.y][self.x].pop(self.get_index(matrix))
                        return False
            for rule in level_rules:
                if ((not rule_object.is_text and f'{rule_object.name} is weak' in rule.text_rule) or
                        (f'text is weak' in rule.text_rule and (rule_object.name in TEXT_ONLY or rule_object.is_text))) \
                        and rule.check_fix(rule_object, matrix, level_rules):
                    matrix[self.y + delta_y][self.x +
                                             delta_x].pop(rule_object.get_index(matrix))
            return True

    def check_shut_open(self, delta_x, delta_y, matrix, level_rules, rule_object) -> bool:
        """Проверяет правилa shut и open у объекта и сразу
        выполняет действие, если возможно

        :param delta_x: Сдвиг объекта по оси x
        :type delta_x: int
        :param delta_y: Сдвиг объекта по оси y
        :type delta_y: int
        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]
        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param rule_object: Объект, с которым движущийся объект
        потенциально может взаимодействовать
        :type rule_object: Object
        :return: True если объект выжил иначе False
        :rtype: bool
        """
        if self.can_interact(rule_object, level_rules):
            if not self.is_safe:
                for rule in level_rules:
                    if not rule_object.is_text and self.is_open and f'{rule_object.name} is shut' in rule.text_rule \
                        or self.is_shut and f'{rule_object.name} is open' in rule.text_rule\
                            and rule.check_fix(rule_object, matrix, level_rules):
                        matrix[self.y][self.x].pop(self.get_index(matrix))
                        matrix[self.y + delta_y][self.x +
                                                 delta_x].pop(rule_object.get_index(matrix))
                        return False
            for rule in level_rules:
                if not rule_object.is_text and self.is_open and f'{rule_object.name} is shut' in rule.text_rule \
                    or self.is_shut and f'{rule_object.name} is open' in rule.text_rule\
                        and rule.check_fix(rule_object, matrix, level_rules):
                    if not self.is_safe:
                        matrix[self.y][self.x].pop(self.get_index(matrix))
                    matrix[self.y + delta_y][self.x +
                                             delta_x].pop(rule_object.get_index(matrix))
                    if not self.is_safe:
                        return False

            return True

    def die(self, delta_j, delta_i, matrix, level_rules):
        self.has_objects = []
        for rule in level_rules:
            if f'{self.name} has' in rule.text_rule:
                self.has_objects.append(rule.text_rule.split()[-1])
        for new_object_name in self.has_objects:
            new_object = Object(
                x=self.x + delta_j,
                y=self.y + delta_i,
                direction=self.direction,
                name=new_object_name,
                is_text=False,
                palette=Palette(self.palette.name, self.palette.pixels.copy())
            )
            new_object.animation = new_object.animation_init()
            matrix[self.y + delta_i][self.x + delta_j].append(new_object)

    def check_defeat(self, delta_x, delta_y, matrix, level_rules, rule_object) -> bool:
        """Проверяет правило defeat у объекта и сразу
        выполняет действие, если возможно

        :param delta_x: Сдвиг объекта по оси x
        :type delta_x: int
        :param delta_y: Сдвиг объекта по оси y
        :type delta_y: int
        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]
        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param rule_object: Объект, с которым движущийся объект
        потенциально может взаимодействовать
        :type rule_object: Object
        :return: True если объект выжил иначе False
        :rtype: bool
        """
        if self.can_interact(rule_object, level_rules):
            if not self.object_can_stop(rule_object, level_rules, matrix, True):
                if not self.is_safe:
                    for rule in level_rules:
                        if ((not rule_object.is_text and f'{rule_object.name} is defeat' in rule.text_rule) or
                                (f'text is defeat' in rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                          or rule_object.name in NOUNS and rule_object.is_text))) \
                                and rule.check_fix(rule_object, matrix, level_rules):
                            for sec_rule in level_rules:
                                if f'{self.name} is you' in sec_rule.text_rule \
                                        and sec_rule.check_fix(self, matrix, level_rules):
                                    matrix[self.y][self.x].pop(
                                        self.get_index(matrix))
                                    return False

                                if f'{self.name} is 3d' in sec_rule.text_rule \
                                        and sec_rule.check_fix(self, matrix, level_rules):
                                    matrix[self.y][self.x].pop(
                                        self.get_index(matrix))
                                    return False

                for rule in level_rules:
                    if f'{self.name} is defeat' in rule.text_rule \
                            and rule.check_fix(self, matrix, level_rules):
                        for sec_rule in level_rules:
                            if (not rule_object.is_text and f'{rule_object.name} is you' in sec_rule.text_rule) or\
                                    (f'text is you' in rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                           or rule_object.name in NOUNS and rule_object.is_text)) \
                                    and sec_rule.check_fix(rule_object, matrix, level_rules):
                                matrix[self.y + delta_y][self.x +
                                                         delta_x].pop(rule_object.get_index(matrix))
                            elif not rule_object.is_text and f'{rule_object.name} is 3d' in sec_rule.text_rule \
                                    and sec_rule.check_fix(rule_object, matrix, level_rules):
                                matrix[self.y + delta_y][self.x +
                                                         delta_x].pop(rule_object.get_index(matrix))
            return True

    def check_sink(self, delta_x, delta_y, matrix, level_rules, rule_object) -> bool:
        """Проверяет правило sink у объекта и сразу
        выполняет действие, если возможно

        :param delta_x: Сдвиг объекта по оси x
        :type delta_x: int
        :param delta_y: Сдвиг объекта по оси y
        :type delta_y: int
        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]
        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param rule_object: Объект, с которым движущийся объект
        потенциально может взаимодействовать
        :type rule_object: Object
        :return: True если объект выжил иначе False
        :rtype: bool
        """
        if self.can_interact(rule_object, level_rules):
            if not self.object_can_stop(rule_object, level_rules, matrix, True):
                if not self.is_safe:
                    for rule in level_rules:
                        if ((f'{rule_object.name} is sink' in rule.text_rule and not rule_object.is_text) or
                            (f'text is sink' in rule.text_rule and (rule_object.name in TEXT_ONLY
                                                                    or rule_object.name in NOUNS and rule_object.is_text))) \
                                and rule.check_fix(rule_object, matrix, level_rules):
                            matrix[self.y][self.x].pop(self.get_index(matrix))
                            matrix[self.y + delta_y][self.x +
                                                     delta_x].pop(rule_object.get_index(matrix))
                            return False
                for rule in level_rules:
                    if ((f'{self.name} is sink' in rule.text_rule and not self.is_text) or
                            (f'text is sink' in rule.text_rule and (self.name in TEXT_ONLY
                                                                    or self.name in NOUNS and self.is_text)))\
                            and rule.check_fix(self, matrix, level_rules):
                        matrix[self.y + delta_y][self.x +
                                                 delta_x].pop(rule_object.get_index(matrix))
            return True

    def check_win(self, level_rules, rule_object, matrix) -> bool:
        """Проверяет правило win у объекта и сразу
        выполняет действие, если возможно. В случае победы
        возвращает игрока в предыдущее меню.

        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param rule_object: Объект, с которым движущийся объект
        потенциально может взаимодействовать
        :type rule_object: Object
        :return: True если победа достигнута иначе False
        :rtype: bool
        """
        if self.can_interact(rule_object, level_rules):
            if not self.object_can_stop(rule_object, level_rules, matrix, True):
                for rule in level_rules:
                    if ((f'{rule_object.name} is win' in rule.text_rule and not rule_object.is_text) or
                        (f'text is win' in rule.text_rule and (rule_object.name in TEXT_ONLY
                                                               or rule_object.name in NOUNS and rule_object.is_text))) \
                            and rule.check_fix(rule_object, matrix, level_rules):
                        for sec_rule in level_rules:

                            if ((f'{self.name} is you' in sec_rule.text_rule and not self.is_text) or
                                    (f'text is you' in sec_rule.text_rule and (self.name in TEXT_ONLY
                                                                               or self.name in NOUNS and self.is_text))) \
                                    and rule.check_fix(self, matrix, level_rules) or \
                                ((f'{self.name} is 3d' in sec_rule.text_rule and not self.is_text) or
                                 (f'text is 3d' in sec_rule.text_rule and (self.name in TEXT_ONLY
                                                                           or self.name in NOUNS and self.is_text))) \
                                    and rule.check_fix(self, matrix, level_rules):
                                if not self.level_processor.flag_to_win_animation \
                                        and not self.level_processor.flag_to_level_start_animation:
                                    self.level_processor.flag_to_win_animation = True
            return False

    def check_rules(self, delta_x, delta_y, matrix, level_rules, rule_object) -> Literal[True]:
        """Проверяет все правила, действующие на объект
        И меняет его статус в зависимости от них

        :param delta_x: Сдвиг объекта по оси x
        :type delta_x: int
        :param delta_y: Сдвиг объекта по оси y
        :type delta_y: int
        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]
        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param rule_object: Объект, с которым движущийся объект
        потенциально может взаимодействовать
        :type rule_object: Object
        :return: True "Так нужно" (c)Vlastelin
        :rtype: bool
        """
        self.status = 'alive'
        if self.can_interact(rule_object, level_rules):
            self.check_win(level_rules, rule_object, matrix)

            if not self.check_melt(delta_x, delta_y, matrix, level_rules, rule_object) or \
                    not self.check_shut_open(delta_x, delta_y, matrix, level_rules, rule_object) or \
                    not self.check_defeat(delta_x, delta_y, matrix, level_rules, rule_object) or \
                    not self.check_sink(delta_x, delta_y, matrix, level_rules, rule_object) or \
                    not self.check_weak(delta_x, delta_y, matrix, level_rules, rule_object):
                self.status = 'dead'

            elif self.check_swap(delta_x, delta_y, matrix, level_rules, rule_object):
                self.status = 'moved_swap'

        return True

    def object_can_stop(self, rule_object, level_rules, matrix, with_push=False) -> bool:
        """Проверяет требуется ли обработка коллизий с объектом

        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param rule_object: Объект, с которым движущийся объект
        потенциально может взаимодействовать
        :type rule_object: Object
        :param with_push: Пытаются ли толкнуть объект
        :type with_push: bool
        :return: True если объект обрабатывает коллизии иначе False
        :rtype: bool
        """
        status = False
        for rule in level_rules:
            if (f'{rule_object.name} is stop' in rule.text_rule and not rule_object.is_text
                or f'{rule_object.name} is pull' in rule.text_rule and not rule_object.is_text
                or (f'text is pull' in rule.text_rule and (rule_object.name in TEXT_ONLY or rule_object.is_text))) \
                    and self.can_interact(rule_object, level_rules) and rule.check_fix(rule_object, matrix, level_rules):
                status = True
            if with_push:
                if f'{rule_object.name} is push' in rule.text_rule and not rule_object.is_text \
                        or (rule_object.name in TEXT_ONLY
                            or rule_object.name in NOUNS and rule_object.is_text) \
                        and rule.check_fix(rule_object, matrix, level_rules)\
                        and self.can_interact(rule_object, level_rules, True):
                    status = True
        return status

    def object_can_move(self, level_rules) -> bool:
        """Проверяет может ли звигаться объект в зависимости от правил
        !!! Такая интерпритация быстрее проверки через лист

        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :return: Может ли двигаться объект
        :rtype: bool
        """
        status = False
        moveable_rules_list = [
            f'{self.name} is move',
            f'{self.name} is push',
            f'{self.name} is auto',
            f'{self.name} is nudge',
            f'{self.name} is chill',
            f'{self.name} is you',
            f'{self.name} is you2',
            f'{self.name} is fall',
            f'{self.name} is 3d',
        ]
        for rule in level_rules:
            if rule.text_rule in moveable_rules_list or \
                    (self.name in TEXT_ONLY
                     or self.name in NOUNS and self.is_text) and \
                    self.check_valid_range(0, 0):
                status = True
        return status

    def check_valid_range(self, delta_x, delta_y) -> bool:
        """Проверяет выход за границы матрицы
        в процессе движения

        :param delta_x: Сдвиг объекта по оси x
        :type delta_x: int
        :param delta_y: Сдвиг объекта по оси y
        :type delta_y: int
        :return: Можно ли двигаться в данном направлении
        :rtype: bool
        """
        return self.level_size[0] - 1 >= self.x + delta_x >= 0 \
            and self.level_size[1] - 1 >= self.y + delta_y >= 0

    def pull_objects(self, delta_x, delta_y, matrix, level_rules) -> None:
        """Тянет объекты с правилом pull

        :param delta_x: Сдвиг объекта по оси x
        :type delta_x: int
        :param delta_y: Сдвиг объекта по оси y
        :type delta_y: int
        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]
        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        """
        if self.check_valid_range(-delta_x, -delta_y):
            for rule_object in matrix[self.y - delta_y][self.x - delta_x]:
                if not rule_object.is_text and rule_object.name in NOUNS:
                    for rule in level_rules:
                        if (f'{rule_object.name} is pull' in rule.text_rule
                            or (f'text is pull' in rule.text_rule and (rule_object.name in TEXT_ONLY or rule_object.is_text))) \
                                and rule.check_fix(rule_object, matrix, level_rules):
                            rule_object.motion(
                                delta_x, delta_y, matrix, level_rules, 'pull')

    def check_locked(self, delta_x, delta_y) -> bool:
        """Блокирует стороны для движения в случае
        выхода за границы матрицы этим движением

        :param delta_x: Сдвиг объекта по оси x
        :type delta_x: int
        :param delta_y: Сдвиг объекта по оси y
        :type delta_y: int
        :return: Можно ли двигаться объекту в
        сторону его нынешнего движения
        :rtype: bool
        """
        side = self.find_side(delta_x, delta_y)
        if side == 'up' and self.y == 0:
            self.locked_sides.append('up')
        elif side == 'left' and self.x == 0:
            self.locked_sides.append('left')
        elif side == 'right' and self.x == self.level_size[0] - 1:
            self.locked_sides.append('right')
        elif side == 'down' and self.y == self.level_size[1] - 1:
            self.locked_sides.append('down')
        if side in self.locked_sides:
            return False
        return True

    def can_interact(self, rule_object, level_rules, status_push=False) -> bool:
        """Можно ли взаимодействовать с объектом
        (проверка на правило float)

        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param rule_object: Объект, с которым движущийся объект
        потенциально может взаимодействовать
        :type rule_object: Object
        :return: Может ли движущийся объект взаимодействовать с данным
        :rtype: bool
        """
        status_float_rule_object = False
        status_push_rule_object = False
        self.is_float = False
        for rule in level_rules:
            if (f'{rule_object.name} is float' == rule.text_rule and not rule_object.is_text) or \
                (f'text is float' == rule.text_rule and (rule_object.name in TEXT_ONLY
                                                         or rule_object.is_text)):
                status_float_rule_object = True
            if status_push:
                if (f'{rule_object.name} is push' in rule.text_rule
                        and not ((rule_object.name in TEXT_ONLY
                                  or rule_object.name in NOUNS and rule_object.is_text))) \
                        or (rule_object.name in TEXT_ONLY or rule_object.is_text):
                    status_push_rule_object = True
            if (f'{self.name} is float' == rule.text_rule and not self.is_text) or \
                (f'text is float' == rule.text_rule and (self.name in TEXT_ONLY
                                                         or self.is_text)):
                self.is_float = True
        if self.is_float == status_float_rule_object \
                or status_push_rule_object:
            return True
        return False

    def motion(self, delta_x, delta_y, matrix, level_rules, status=None) -> bool:
        """Осуществляет движение объектаd
        :param delta_x: Сдвиг объекта по оси x
        :type delta_x: int
        :param delta_y: Сдвиг объекта по оси y
        :type delta_y: int
        :param matrix: Матрица, на которой расположен объект
        :type matrix: List[List[List[Object]]]
        :param level_rules: Правила уровня в момент движения
        :type level_rules: List[TextRule]
        :param status: статус объекта, defaults to None
        :type status: str, optional
        :return: Сдвинется ли объект
        :rtype: bool
        """
        if self.check_locked(delta_x, delta_y) and not self.is_sleep and len(matrix[self.y][self.x]) > 0:
            for rule_object in matrix[self.y + delta_y][self.x + delta_x]:
                self.check_rules(delta_x, delta_y, matrix,
                                 level_rules, rule_object)
            if self.status == 'dead':
                self.die(delta_x, delta_y, matrix, level_rules)
                return True
            if self.status == 'moved_swap':
                return False
            for rule_object in matrix[self.y + delta_y][self.x + delta_x]:
                if rule_object.object_can_stop(rule_object, level_rules, matrix) \
                        and self.can_interact(rule_object, level_rules):
                    return False
            status_motion = 'no collision'
            if self.status == 'alive':
                for rule_object in matrix[self.y + delta_y][self.x + delta_x]:
                    if (self.is_phantom or not rule_object.object_can_stop(rule_object, level_rules, matrix, True)
                            or not self.can_interact(rule_object, level_rules, True)) and status_motion is not False:
                        if self.object_can_move(level_rules) and not self.is_still:
                            status_motion = True

                    elif self.is_fall:
                        status_motion = False

                    elif self.object_can_move(level_rules) \
                            and not self.is_still \
                            and status_motion is not False:
                        status_motion = rule_object.motion(
                            delta_x, delta_y, matrix, level_rules, 'push')

                if status_motion is True:
                    matrix[self.y][self.x].pop(self.get_index(matrix))
                    self.pull_objects(delta_x, delta_y,
                                      matrix, level_rules)
                    self.update_parameters(delta_x, delta_y, matrix)
                    return True
                if status_motion is False:
                    return False

            for rule in level_rules:
                if f'{self.name} is push' in rule.text_rule and status == 'push' and not self.is_text \
                        and rule.check_fix(self, matrix, level_rules):
                    matrix[self.y][self.x].pop(self.get_index(matrix))
                    self.update_parameters(delta_x, delta_y, matrix)
                    return True

            for rule in level_rules:
                if ((f'{self.name} is stop' in rule.text_rule and status == 'push')
                    or (f'{self.name} is pull' in rule.text_rule and status == 'push')) \
                        and not self.is_text \
                        and rule.check_fix(self, matrix, level_rules):
                    return False

            if status is None or (self.name in TEXT_ONLY
                                  or self.name in NOUNS and self.is_text):
                matrix[self.y][self.x].pop(self.get_index(matrix))
                self.pull_objects(delta_x, delta_y, matrix, level_rules)
                self.update_parameters(delta_x, delta_y, matrix)

            for rule in level_rules:
                if ((f'{self.name} is pull' in rule.text_rule and status == 'pull' and not self.is_text) or
                    (f'text is pull' in rule.text_rule and (self.name in TEXT_ONLY or self.is_text)))\
                        and rule.check_fix(self, matrix, level_rules):
                    matrix[self.y][self.x].pop(self.get_index(matrix))
                    self.pull_objects(delta_x, delta_y, matrix, level_rules)
                    self.update_parameters(delta_x, delta_y, matrix)

            return True
        elif DEBUG:
            print(
                "NOTE: Object can not move. Calling from classes/objects.py->Object.motion()")
        return False

    def check_word(self, level_rules):
        for rule in level_rules:
            if f'{self.name} is word' in rule.text_rule:
                return True
        return False

    def check_events(self, events: List[pygame.event.Event], number):
        """Метод обработки событий

        :param events: События, полученные при выхове
        :type events: List[pygame.event.Event]
        :param number: Номер правила YOU объекта (/YOU2)
        :type number: int
        """
        self.turning_side = get_pressed_direction(number == 2)

    def text(self, rule, property):
        return (f'text {property}' in rule.text_rule and (self.name in OPERATORS
                                                          or self.name in PROPERTIES
                                                          or self.name in TEXT_ONLY
                                                          or (self.name in NOUNS and self.is_text)))

    @property
    def is_operator(self) -> bool:
        """Является ли объект оператором

        :return: Является ли объект оператором
        :rtype: bool
        """
        return self.name in OPERATORS

    @property
    def is_property(self) -> bool:
        """Является ли объект свойством

        :return: Является ли объект свойством
        :rtype: bool
        """
        return self.name in PROPERTIES

    @property
    def is_noun(self) -> bool:
        """Является ли объект существительным

        :return: Является ли объект существительным
        :rtype: bool
        """
        return (self.name in NOUNS and self.name not in OPERATORS and self.is_text) or self.name in 'text'

    @property
    def special_text(self) -> bool:
        """Является ли объект текстом, но тут проперти особенный

        :return: Является ли объект текстом
        :rtype: bool
        """
        return self.is_text

    def __copy__(self):
        """Метод копирования объекта

        :return: Копия объекта
        :rtype: Object
        """
        copied_object = Object(
            x=self.x,
            y=self.y,
            direction=self.direction,
            name=self.name,
            is_text=self.is_text,
            palette=Palette(self.palette.name, self.palette.pixels.copy()),
            movement_state=self.movement_state,
            neighbours=None,
            turning_side=self.turning_side,
            animation=self.animation,
            safe=self.is_safe,
            angle_3d=self.angle_3d,
            is_3d=self.is_3d,
            moved=self.moved,
            num_3d=self.num_3d,
            level_size=self.level_size,
            smooth_movement=self._movement
        )
        copied_object.is_sleep = self.is_sleep
        return copied_object

    def __repr__(self):
        result = "text " if self.is_text else ""
        result += self.name
        result += f" {self.x};{self.y}"
        return result
