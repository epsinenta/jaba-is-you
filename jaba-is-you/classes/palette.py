from dataclasses import dataclass
from typing import List

import pygame

from global_types import COLOR, SURFACE


@dataclass
class Palette:
    name: str
    pixels: List[List[COLOR]]  # pixels[1][2] - x: 2, y: 1

    def draw(self, screen: SURFACE, pixel_size: int, x_pixel_offset: int, y_pixel_offset: int):
        """
        Отрисовка пикселей палитры

        :param screen: Экран на котором будут отрисовываться пиксели
        :param pixel_size: Размер пикселей
        :param x_pixel_offset: Отступ отрисовки по оси абсциссы
        :param y_pixel_offset: Отступ отрисовки по оси ординат
        """
        blit_sequences = []
        for y_palette_pixel, line in enumerate(self.pixels):
            for x_palette_pixel, pixel_color in enumerate(line):
                pixel_surface = pygame.surface.Surface(
                    (pixel_size, pixel_size))
                pixel_surface.fill(pixel_color)
                pixel_surface = pixel_surface.convert(screen)
                position = (
                    x_pixel_offset + x_palette_pixel * pixel_size,
                    y_pixel_offset + y_palette_pixel * pixel_size,
                )
                blit_sequences.append(
                    (pixel_surface, position, pygame.rect.Rect(0, 0, pixel_size, pixel_size)))
        screen.blits(blit_sequences, doreturn=0)
