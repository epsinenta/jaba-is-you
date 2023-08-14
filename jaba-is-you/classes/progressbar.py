from typing import Optional

import pygame

from global_types import COLOR, SURFACE
from utils import map_value


class ProgressBar:
    def __init__(
            self,
            left: int, top: int, width: int, height: int,
            border_color: COLOR, left_right_border_size: int, up_down_border_size: int,
            progress_color: COLOR, progress_min: float, progress_max: float,
            progress_background_color: COLOR
    ):
        self.progress_background_color: COLOR = progress_background_color
        self.rect = pygame.rect.Rect(left, top, width, height)
        self.border_color: COLOR = border_color
        self.left_right_border_size: int = left_right_border_size
        self.up_down_border_size: int = up_down_border_size
        self.progress_color: COLOR = progress_color
        self.progress_min: float = progress_min
        self.progress_max: float = progress_max
        self._progress: float = 0
        self._old_progress_width: Optional[float] = None

    @property
    def progress(self) -> float:
        return self._progress

    @progress.setter
    def progress(self, value: float):
        self._progress = value

    @property
    def left(self) -> int:
        return self.rect.left

    @left.setter
    def left(self, value: int):
        self.rect.left = value

    @property
    def top(self) -> int:
        return self.rect.top

    @top.setter
    def top(self, value: int):
        self.rect.top = value

    @property
    def width(self) -> int:
        return self.rect.width

    @width.setter
    def width(self, value: int):
        self.rect.width = value

    @property
    def height(self) -> int:
        return self.rect.height

    @height.setter
    def height(self, value: int):
        self.rect.height = value

    def draw(self, screen: SURFACE):
        progress_width = map_value(self._progress, self.progress_min, self.progress_max,
                                   0, self.width - self.left_right_border_size * 2)
        if self._old_progress_width is None or self._old_progress_width != progress_width:
            pygame.draw.rect(screen, self.border_color, pygame.rect.Rect(
                self.left - self.left_right_border_size, self.top - self.up_down_border_size,
                self.width + self.left_right_border_size, self.height + self.up_down_border_size
            ))
            pygame.draw.rect(screen, self.progress_background_color, pygame.rect.Rect(
                self.left + self.left_right_border_size, self.top,
                self.width - self.left_right_border_size * 2,
                self.height - self.up_down_border_size
            ))
            pygame.draw.rect(screen, self.progress_color, pygame.rect.Rect(
                self.left + self.left_right_border_size, self.top,
                progress_width, self.height - self.up_down_border_size
            ))
            self._old_progress_width = progress_width
            return True
        return False
