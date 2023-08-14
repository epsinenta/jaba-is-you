from typing import Union, TYPE_CHECKING, Callable, Any, Optional, List, Sequence, Tuple

import pygame

if TYPE_CHECKING:
    from global_types import SURFACE


class Slider:
    """
    Класс ползунка

    :ivar x: Абсцисса положения в пикселях
    :ivar y: Ордината положения в пикселях
    :ivar width: Ширина в пикселях
    :ivar height: Высота в пикселях
    :ivar color_rect: Цвет полоски
    :ivar circle_center: Центр кружочка
    :ivar radius: Радиус кружочка
    :ivar color_circle: Цвет кружочка
    :ivar action: Функция вызывающаяся при нажатии
    """

    def __init__(self, xpx: float, ypx: float, width: float, height: float, color_rect,
                 circle_center: Tuple[float, float],
                 radius: float, color_circle, action: Optional[Callable[[], Any]]):
        """
        Инициализация ползунка

        :ivar x: Абсцисса положения в пикселях
        :ivar y: Ордината положения в пикселях
        :ivar width: Ширина в пикселях
        :ivar height: Высота в пикселях
        :ivar color_rect: Цвет полоски
        :ivar circle_center: Центр кружочка
        :ivar radius: Радиус кружочка
        :ivar color_circle: Цвет кружочка
        :ivar action: Функция вызывающаяся при нажатии
        """
        self.xpx = xpx
        self.ypx = ypx
        self.width = width
        self.height = height
        self.color_rect = color_rect
        self.circle_center = circle_center
        self.radius = radius
        self.color_circle = color_circle
        self.action = action
        self.flag_action = False

    def draw(self, screen: "SURFACE"):
        """
        Метод отрисовки ползунка

        :param screen: Surface, на котором будет происходить отрисовка
        """
        pygame.draw.rect(screen, self.color_rect, (self.xpx, self.ypx, self.width, self.height), 0)
        pygame.draw.circle(screen, self.color_circle, self.circle_center, self.radius)

    def update(self, events: List[pygame.event.Event]):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN \
                    and self.is_over(pygame.mouse.get_pos()):
                self.flag_action = True
            if event.type == pygame.MOUSEBUTTONUP and self.flag_action:
                self.flag_action = False
        if self.flag_action and self.action:
            self.action()

    def is_over(self, pos: Sequence[Union[int, float]]) -> bool:
        """
        Проверка координат на нахождение внутри области ползунка

        :param pos: Абсцисса и Ордината для проверки наведения

        :return: True, если Абсцисса и Ордината находится в области кнопки, иначе False.
        """
        if self.xpx < pos[0] < self.xpx + self.width:
            if self.ypx < pos[1] < self.ypx + self.height:
                return True
        return False
