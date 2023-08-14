from typing import Final, TYPE_CHECKING, Callable, List, Union, Type

import pygame

import settings
from classes.game_state import GameState
from elements.global_classes import language_manager
from global_types import SURFACE
from settings import FRAMES_PER_SECOND, DEBUG
from utils import settings_saves

if TYPE_CHECKING:
    from classes.game_strategy import GameStrategy


class GameContext:
    """
    Основной класс игры вокруг которого всё будет крутиться.

    :ivar screen: Экран на котором будет всё отрисовываться
    """

    def __init__(self, game_strategy: Union[Callable[[SURFACE], "GameStrategy"], Type["GameStrategy"]]):
        """
        Инициализация класса

        :param game_strategy: GameStrategy которая будет отрисовываться по умолчанию.
        """
        saves = settings_saves()
        if saves[3] == 0:
            settings.RESOLUTION = (1600, 900)
        else:
            settings.RESOLUTION = (800, 450)
        settings.WINDOW_SCALE = saves[4]
        language_manager.current_language = saves[1]
        self.screen: Final[SURFACE] = pygame.display.set_mode(
            settings.RESOLUTION)
        self._running: bool = True
        self._history: List["GameStrategy"] = []

        self._game_strategy: "GameStrategy"
        self.game_strategy = game_strategy  # type: ignore
        # См. https://github.com/python/mypy/issues/3004

        pygame.init()
        pygame.font.init()
        pygame.mixer.init()

    @property
    def game_strategy(self) -> "GameStrategy":
        """
        :setter: Устанавливает :class:`classes.game_strategy.GameStrategy` в игру

        :getter: Возвращает текущую :class:`classes.game_strategy.GameStrategy`
        """
        return self._game_strategy

    @game_strategy.setter
    def game_strategy(self, game_strategy: Union[Callable[[SURFACE], "GameStrategy"], "GameStrategy"]):
        if callable(game_strategy):
            self._game_strategy = game_strategy(self.screen)
        else:
            self._game_strategy = game_strategy
        if len(self._history) > 1 and self._history[-2] == self._game_strategy:
            del self._history[-1]
        else:
            self._history.append(self._game_strategy)
        if DEBUG:
            print(
                f'Current game strategy is {self._game_strategy.__class__.__name__}; History a.k.a stack: ', end="")
            print(
                [game_strategy.__class__.__name__ for game_strategy in self._history], indent=4)

    @property
    def running(self) -> bool:
        """
        :setter: Устанавливает переменную в основном цикле игры. Если False игра выключится

        :return: Запущена ли игра?
        """
        return self._running

    @running.setter
    def running(self, value: bool):
        self._running = value

    @property
    def history(self) -> List["GameStrategy"]:
        """
        :setter: Изменять его нельзя, используйте State

        :return: Стек вызовов GameStrategy, например [MainMenu, MainLevel, Game]
        """
        return self._history

    def run(self):
        """Функция запуска игры"""
        clock = pygame.time.Clock()
        pygame.mixer.music.set_volume(settings_saves()[2])
        while self.running:
            try:
                delta_time = clock.tick(FRAMES_PER_SECOND)
                pygame.display.set_caption(
                    f"FPS: {round(clock.get_fps())} in {self.game_strategy.__class__.__name__} ")
                events = pygame.event.get()
                draw_state = self.game_strategy.draw(events, delta_time)

                if not pygame.mixer.music.get_busy():
                    try:
                        pygame.mixer.music.play()
                    except pygame.error:
                        pass

                if draw_state is not None:
                    if draw_state.game_state is GameState.STOP:
                        raise KeyboardInterrupt
                    if draw_state.game_state is GameState.SWITCH:
                        self.game_strategy = draw_state.switch_to

                        pygame.event.set_blocked(pygame.SYSWMEVENT)
                        # Unknown Windows 10 event that reduces performance

                        self.game_strategy.on_init()
                    elif draw_state.game_state is GameState.FLIP:
                        pygame.display.flip()
                    elif draw_state.game_state is GameState.BACK:
                        if len(self.history) > 1:
                            self.game_strategy = self.history[-2]

                            pygame.event.set_blocked(pygame.SYSWMEVENT)
                            # Unknown Windows 10 event that reduces performance

                            self.game_strategy.on_init()
                        else:
                            raise ValueError(
                                "Can't back; Use debug to show the history of strategies; ")
                    else:
                        raise ValueError(
                            f"draw_state.game_state: {draw_state.game_state}. WTF is this!?")
            except KeyboardInterrupt:
                self.running = False
