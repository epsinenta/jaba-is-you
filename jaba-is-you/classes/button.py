from typing import Union, TYPE_CHECKING, Callable, Any, Optional, List, Sequence

import pygame

import settings

if TYPE_CHECKING:
    from elements.global_classes import AbstractButtonSettings
    from global_types import COLOR, SURFACE


class Button:
    """
    Класс кнопки

    :ivar x: Абсцисса положения
    :ivar y: Ордината положения
    :ivar width: Ширина в пикселях
    :ivar height: Высота в пикселях
    :ivar outline: Цвет контура
    :ivar settings: Настройка цветов
    :ivar text: Текст
    :ivar action: Функция вызывающаяся при нажатии
    """

    def __init__(self, x: int, y: int, width: int, height: int, outline: "COLOR",
                 button_settings: "AbstractButtonSettings",
                 text: str = "", action: Optional[Callable[[], Any]] = None):
        """
        Инициализация кнопки

        :param x: Абсцисса положения
        :param y: Ордината положения
        :param width: Ширина в пикселях
        :param height: Высота в пикселях
        :param outline: Цвет контура
        :param button_settings: Настройка цветов
        :param text: Текст
        :param action: Функция вызывающаяся при нажатии
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.scale = settings.WINDOW_SCALE
        self.settings = button_settings
        self.action = action
        self.outline = outline

    def draw(self, screen: "SURFACE"):
        """
        Метод отрисовки кнопки

        :param screen: Surface, на котором будет происходить отрисовка
        """
        if self.outline:
            pygame.draw.rect(screen, self.outline, (self.x - 2,
                                                    self.y - 2, self.width + 4, self.height + 4), 0)

        color = self.settings.button_color if not self.is_over(
            pygame.mouse.get_pos()) else self.settings.button_color_hover
        pygame.draw.rect(screen, color, (self.x, self.y,
                                         self.width, self.height), 0)

        if self.text != "":
            pygame.font.init()
            font = pygame.font.Font(
                "fonts/ConsolateElf.ttf", int(self.settings.text_size * self.scale))
            lines = self.text.split('\n')
            text_height = 0
            for index, line in enumerate(lines):
                render_line = font.render(line, True, self.settings.text_color)
                text_height += render_line.get_height()
                screen.blit(
                    render_line,
                    (
                        self.x + (self.width / 2 -
                                  render_line.get_width() / 2),
                        self.y + (self.height / 2 + (text_height / len(lines) *
                                                     (len(lines) // 2 * -1 + index))) -
                        (render_line.get_height() / 2 if len(lines) == 1 else 0)
                    )
                )

    def update(self, events: List[pygame.event.Event]) -> bool:
        """
        Метод проверки нажатия.

        :param events: Список событий полученных путём вызова pygame.event.get()
        :return: В случае если был вызван action, True, иначе False
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN \
                    and self.is_over(pygame.mouse.get_pos()) \
                    and self.action:
                self.action()
                return True
        return False

    def is_over(self, pos: Sequence[Union[int, float]]) -> bool:
        """
        Проверка координат на нахождение внутри области кнопки

        :param pos: Абсцисса и Ордината для проверки наведения

        :return: True, если Абсцисса и Ордината находится в области кнопки, иначе False.
        """
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
        return False
