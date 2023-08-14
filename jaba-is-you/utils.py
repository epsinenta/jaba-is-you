from copy import copy
from typing import Final, Literal, Dict

import os
import pygame


def my_deepcopy(arr):
    """Полное копирование трёхмерного массива без использования указателей

    :param arr: Исходный массив
    :type arr: list
    :return: Копия в других ячейках памяти
    :rtype: list
    """
    new_arr = []
    for val in arr:
        if isinstance(val, list):
            new_arr.append(my_deepcopy(val))
        else:
            new_arr.append(copy(val))
    return new_arr


def get_pressed_direction(arrows: bool = False) -> \
        Literal[-1, 0, 1, 2, 3]:
    """Метод обработки клавиш поворота чего-либо"""
    side_and_key: Dict[int, Literal[0, 1, 2, 3]]
    if arrows:
        side_and_key = {
            pygame.K_RIGHT: 0,
            pygame.K_UP: 1,
            pygame.K_LEFT: 2,
            pygame.K_DOWN: 3
        }
    else:
        side_and_key = {
            pygame.K_d: 0,
            pygame.K_w: 1,
            pygame.K_a: 2,
            pygame.K_s: 3
        }
    bad: Final[Literal[-1]] = -1
    turning_side: Literal[-1, 0, 1, 2, 3] = bad
    for key in side_and_key.keys():
        if pygame.key.get_pressed()[key]:
            turning_side = side_and_key[key]
            # break
    return turning_side


def settings_saves():
    options = []
    if os.path.exists('saves/option_settings'):
        with open('saves/option_settings', mode='r', encoding='utf-8') as saves:
            for param in saves:
                options.append(param.strip())
        if options[0] == 'False':
            options[0] = False
        else:
            options[0] = True
        options[1] = str(options[1])
        options[2] = float(options[2])
        options[3] = int(options[3])
        options[4] = float(options[4])
    else:
        options.append(True)
        options.append('eng')
        options.append(1.0)
        options.append(0)
        options.append(1.0)
    return options


def map_value(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def map_saves():
    open_levels = {}
    with open('saves/map_saves', mode='r', encoding='utf-8') as saves:
        for lev in saves.readlines():
            lev = lev.strip().split()
            open_levels[lev[0]] = int(lev[1])
    return open_levels
