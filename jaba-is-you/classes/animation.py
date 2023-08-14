from typing import List, Tuple, Dict

import pygame

from global_types import SURFACE

# Вот как мне не нравится всё это. ключ - задержка, значение - время
_sync: Dict[int, int] = {}


class Animation:
    """
    Класс анимации

    :ivar sprites: Список картинок которые будут меняться каждые :attr:`~.Animation.sprite_switch_delay`
    :ivar sprite_switch_delay: Задержка в миллисекундах между кадрами
    :ivar position: Позиция в пикселях где будет отрисовываться
    :ivar synchronize: Синхронизировать с остальными анимациями, чтобы кадры менялись одновременно в всех анимациях.
    """

    def __init__(self, sprites: List[pygame.surface.Surface], sprite_switch_delay: int,
                 position: Tuple[int, int], synchronize: bool = True):
        """
        Инициализация анимации

        :param sprites:  Список картинок которые будут меняться каждые **sprite_switch_delay**
        :param sprite_switch_delay: Задержка в миллисекундах между кадрами
        :param position: Позиция в пикселях где будет отрисовываться
        :param synchronize:
            Синхронизировать ли с остальными анимациями, чтобы кадры менялись одновременно в всех анимациях.
        """
        # quswadress: Под чем я был когда писал это?
        # if len(sprites) == 0:
        #     raise ValueError("Sprites are empty")
        self.position: Tuple[int, int] = position
        self.sprites: List[pygame.surface.Surface] = sprites
        self.sprite_switch_delay: int = sprite_switch_delay
        self._current_sprites_index: int = 0
        self.synchronize = synchronize
        if synchronize:
            if self.sprite_switch_delay not in _sync:
                _sync[self.sprite_switch_delay] = pygame.time.get_ticks()
            self._timer = _sync[self.sprite_switch_delay]
        else:
            self._timer = pygame.time.get_ticks()

    @property  # Danilado: Не слишком ли длинное имя для property?
    # quswadress: Длинное имя? Извините, в следующий раз буду называть _, csi, или просто i, а вы сами будете додумывать
    # ...для чего этот i нужен. А если серьёзно, то сокращения порой непонятны, я придерживаюсь принципа:
    # ...много букв, зато сразу понятно. Скажи спасибо что я назвал GameStrategy именно так, а не
    # ...AbstractGameGraphicalUserInterfaceStrategy, или же
    # ...абстрактная стратегия игрового графического пользовательского интерфейса.
    def current_sprites_index(self) -> int:
        """
        :getter: Возвращает текущий номер элемента в :attr:`~.Animation.sprites` который отрисовывается на экране

        :setter:
            Устанавливает текущий номер элемента который отрисовывается на экране в :attr:`~.Animation.sprites`,
            если номер > длины :attr:`~.Animation.sprites`, или номер отрицательный, возбуждается исключение
        """
        return self._current_sprites_index

    @current_sprites_index.setter
    def current_sprites_index(self, value: int):
        if value > len(self.sprites) or value < 0:
            raise ValueError("current sprites index should be lower than length of sprites. "
                             "You might want to use `% len(object.sprites)`")
        self._current_sprites_index = value

    @property
    def current_sprite(self) -> pygame.surface.Surface:
        """
        :getter: Возвращает текущий спрайт который отрисовывается на экране

        :setter:
            Устанавливает текущий спрайт который отрисовывается на экране в :attr:`~.Animation.sprites`,
            если спрайта не существует в :attr:`~.Animation.sprites`, тогда возбуждается исключение.
        """
        return self.sprites[self.current_sprites_index]

    @current_sprite.setter
    def current_sprite(self, value: pygame.Surface):
        try:
            index = self.sprites.index(value)
        except ValueError as error:
            raise ValueError("current sprite should be in sprites") from error
        self.current_sprites_index = index

    def __copy__(self) -> "Animation":
        copy = Animation(
            self.sprites.copy(), self.sprite_switch_delay, self.position, self.synchronize)
        copy._timer = self._timer
        copy.current_sprites_index = self.current_sprites_index
        return copy

    @property
    def is_need_to_switch_frames(self) -> bool:
        return pygame.time.get_ticks() - self._timer >= self.sprite_switch_delay

    def update(self) -> bool:
        """
        Обновление :attr:`~.Animation.current_sprite`.
        """
        if self.is_need_to_switch_frames:
            if self.synchronize:
                _sync[self.sprite_switch_delay] = pygame.time.get_ticks()
                self._timer = _sync[self.sprite_switch_delay]
            else:
                self._timer = pygame.time.get_ticks()
            self.current_sprites_index = (
                self._current_sprites_index + 1) % len(self.sprites)
            return True
        return False

    def draw(self, screen: SURFACE) -> None:
        """
        Отрисовка :attr:`~.Animation.current_sprite` на :attr:`~.Animation.position` в ``screen``

        :param screen: Экран на котором будет отрисовываться :attr:`~.Animation.current_sprite`
        :return:
        """
        screen.blit(self.current_sprite, self.position)
