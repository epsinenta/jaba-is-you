"""Модуль класса партикла"""
import os
from math import sin, cos
from random import randint, uniform
from typing import Optional, Tuple, Union

import pygame

from elements.global_classes import sprite_manager
from global_types import COLOR
from settings import DEBUG


class ParticleStrategy:
    """Класс стратегии движения партикла"""

    def __init__(self, x_dimensions: Optional[Tuple[int, int]] = None, y_dimensions: Optional[Tuple[int, int]] = None,
                 size: Optional[Tuple[int, int]] = None, rotation: Optional[Tuple[int, int]] = None, wobble: int = 0,
                 duration: Optional[float] = None, loop: bool = False, randomize_start_values: bool = False):
        """Инициализация стратегии партикла

        :param x_dimensions: координаты x начала и конца движения партикла, defaults to None
        :type x_dimensions: Tuple[int, int], optional
        :param y_dimensions: координаты y начала и конца движения партикла, defaults to None
        :type y_dimensions: Tuple[int, int], optional
        :param size: размер партикла, defaults to None
        :type size: Tuple[int, int], optional
        :param rotation: угол поворота спрайта партикла в начале и конце движения, defaults to None
        :type rotation: Tuple[int, int], optional
        :param wobble: кол-во пикселей смещения партикла в процессе движение, defaults to 0
        :type wobble: int, optional
        :param duration: Длина анимации в секундах, defaults to None
        :type duration: int, optional
        :param loop: зациклена ли анимация, defaults to False
        :type loop: bool, optional
        :param randomize_start_values: рандомизирует стартовые значения в пределах введённых, defaults to False
        :type randomize_start_values: bool, optional
        """
        try:
            self.duration = duration * 1000
            self.loop = loop
            self.wobble = wobble

            self.x_position = x_dimensions[0]
            self.x_start = x_dimensions[0]
            self.x_offset = x_dimensions[1] - self.x_start

            self.y_position = y_dimensions[0]
            self.y_start = y_dimensions[0]
            self.y_offset = y_dimensions[1] - self.y_start

            self.size = size[0]
            self.size_start = size[0]
            self.size_offset = size[1] - self.size_start

            self.angle = rotation[0]
            self.angle_start = rotation[0]
            self.angle_offset = rotation[1] - self.angle_start

            self.time_randomizer = 0

            if randomize_start_values:
                self.x_position = randint(min(x_dimensions[0], x_dimensions[1]), max(
                    x_dimensions[0], x_dimensions[1]))
                self.y_position = randint(min(y_dimensions[0], y_dimensions[1]), max(
                    y_dimensions[0], y_dimensions[1]))
                self.angle = randint(
                    min(rotation[0], rotation[1]), max(rotation[0], rotation[1]))
                self.time_randomizer = uniform(0, self.duration)

            self.start_timestamp = pygame.time.get_ticks()
        except IndexError:
            if DEBUG:
                print('IndexError в партиклах, ёпта. Что-то не ладно.')
                print(x_dimensions, y_dimensions, rotation, duration, loop)
                print('^ В создание стратегии партикла переданы неправильные аргументы ^')
        except TypeError:
            if DEBUG:
                print('TypeError в партиклах, ёпта. Что-то не ладно.')
                print(x_dimensions, y_dimensions, rotation, duration, loop)
                print('^ В создание стратегии партикла переданы неправильные аргументы ^')

    def update_values(self):
        timestamp = pygame.time.get_ticks()
        time_position = timestamp + self.time_randomizer - self.start_timestamp
        if time_position > self.duration:
            if self.loop:
                self.start_timestamp = timestamp + self.time_randomizer
                self.x_position = self.x_start
                self.y_position = self.y_start
                self.angle = self.angle_start
                self.size = self.size_start
                return self.update_values()
            return False
        time_offset = time_position / self.duration

        self.x_position = self.x_start + self.x_offset * time_offset
        self.y_position = self.y_start + self.y_offset * time_offset

        if self.wobble:
            self.x_position += self.wobble * \
                cos((timestamp+self.time_randomizer)/1000)
            self.y_position += self.wobble * \
                sin((timestamp+self.time_randomizer)/1000)

        self.size = self.size_start + self.size_offset * time_offset

        self.angle = self.angle_start + self.angle_offset * time_offset
        return True


class Particle:
    def __init__(self, name: str = None,
                 strategy: Union[ParticleStrategy, str] = None, color: COLOR = 'white'):
        self.sprite_name = name
        self.color = color

        self.strategy = strategy

        self.sprites_count = len(self._get_sprites())
        self.sprite_index = 0
        self.animation_timestamp = pygame.time.get_ticks()

    def _get_sprites(self):
        path = os.path.join('./', 'sprites', self.sprite_name)
        states = [sprite_manager.get(os.path.join(
            path, name), color=self.color) for name in os.listdir(path)]
        return states

    def update(self):
        if self.strategy.update_values():
            if pygame.time.get_ticks() - self.animation_timestamp >= 200:
                self.sprite_index += 1
                self.sprite_index %= self.sprites_count
                self.animation_timestamp = pygame.time.get_ticks()
            return True
        return False

    def draw(self, screen):
        if self.update():
            screen.blit(
                pygame.transform.scale(
                    pygame.transform.rotate(
                        self._get_sprites()[self.sprite_index], int(self.strategy.angle)),
                    (self.strategy.size, )*2), (self.strategy.x_position, self.strategy.y_position))
            return True
        return False
