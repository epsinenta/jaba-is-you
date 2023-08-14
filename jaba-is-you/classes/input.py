from typing import Union, TYPE_CHECKING, List, Sequence

import pygame

import settings

if TYPE_CHECKING:
    from elements.global_classes import AbstractButtonSettings
    from global_types import COLOR, SURFACE


class Input:
    """Поле ввода текста"""

    def __init__(self, x: int, y: int, width: int, height: int, outline: "COLOR",
                 text_settings: "AbstractButtonSettings", placeholder: str = ""):
        """Инициализация поля ввода

        :param x: Положение поля на экране по оси x
        :type x: int
        :param y: Положение поля на экране по оси y
        :type y: int
        :param width: Ширина поля ввода
        :type width: int
        :param height: Высота поля ввода
        :type height: int
        :param outline: Цвет обводки поля
        :type outline: COLOR
        :param text_settings: Настройки отрисовки и оформления поля ввода
        :type text_settings: AbstractButtonSettings
        :param placeholder:
            Содержимое поля ввода до ввода со стороны игрока, defaults to empty string
        :type placeholder: str, optional
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = ''
        # Это слово пишется слитно, здесь не нужны подчёркивания
        self.placeholder = placeholder
        self.text_settings = text_settings
        self.outline = outline
        self.font = pygame.font.Font(
            "fonts/ConsolateElf.ttf", int(self.text_settings.text_size * settings.WINDOW_SCALE))
        self.focused = False
        self.pressed = False

    def draw(self, screen: "SURFACE"):
        """
        Метод отрисовки поля

        :param screen: Поверхность, на которой будет происходить отрисовка
        """
        if self.outline:
            pygame.draw.rect(screen, self.outline, (self.x - 2,
                             self.y - 2, self.width + 4, self.height + 4), 0)

        self.focused = self.is_over(pygame.mouse.get_pos()) or self.pressed

        color = self.text_settings.button_color if not self.focused else self.text_settings.button_color_hover
        pygame.draw.rect(screen, color, (self.x, self.y,
                         self.width, self.height), 0)

        if self.text != "" or self.placeholder != "":
            if self.pressed or self.text != "":
                lines = (self.text + ('|' if self.pressed else '')).split('\n')
            else:
                lines = self.placeholder.split('\n')

            text_height = 0
            for index, line in enumerate(lines):
                render_line = self.font.render(line, True, (255, 255, 255))
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.pressed = self.is_over(pygame.mouse.get_pos())
            if event.type == pygame.KEYDOWN and self.pressed:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.pressed = False
                else:
                    self.text += pygame.key.name(event.key)
        return self.pressed

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

    def __str__(self):
        return self.text
