import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING

from classes.language_manager import LanguageManager
from classes.palette_manager import PaletteManager
from classes.sound_manager import SoundManager
from classes.sprite_manager import SpriteManager
if TYPE_CHECKING:
    from global_types import COLOR


class AbstractButtonSettings(abc.ABC):
    @property
    @abc.abstractmethod
    def text_size(self) -> int:
        ...

    @property
    @abc.abstractmethod
    def button_color(self) -> "COLOR":
        ...

    @property
    @abc.abstractmethod
    def button_color_hover(self) -> "COLOR":
        ...

    @property
    @abc.abstractmethod
    def text_color(self) -> "COLOR":
        ...


@dataclass
class GuiSettings(AbstractButtonSettings):
    text_size: int = 32
    text_color: "COLOR" = (16, 16, 16)
    button_color: "COLOR" = (255, 255, 255)
    button_color_hover: "COLOR" = (240, 240, 240)


@dataclass
class EuiSettings(AbstractButtonSettings):
    text_size: int = 20
    text_color: "COLOR" = (255, 255, 255)
    button_color: "COLOR" = (0, 0, 0)
    button_color_hover: "COLOR" = (20, 20, 20)


@dataclass
class IuiSettings(AbstractButtonSettings):
    text_size: int = 20
    text_color: "COLOR" = (255, 255, 255)
    button_color: "COLOR" = (0, 0, 0)
    button_color_hover: "COLOR" = (20, 20, 20)


sprite_manager = SpriteManager()
sound_manager = SoundManager()
palette_manager = PaletteManager()
language_manager = LanguageManager()
