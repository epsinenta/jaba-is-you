from dataclasses import dataclass
from typing import TYPE_CHECKING, Union, Callable

from global_types import SURFACE

if TYPE_CHECKING:
    from typing import Optional, Type
    from classes.game_state import GameState
    from classes.game_strategy import GameStrategy


@dataclass
class State:
    """
    Является структурой хранящий дополнительную информацию для GameState,
    например какой GameStrategy необходимо сменить.
    Необходим просто для замены кортежа.

    :cvar game_state: Изменение в :class:`classes.game_context.GameContext`
    :cvar switch_to: Опциональный тип :class:`classes.game_strategy.GameStrategy`.
    """
    game_state: "GameState"
    switch_to: "Optional[Union[Type[GameStrategy], Callable[[SURFACE], GameStrategy]]]" = None
