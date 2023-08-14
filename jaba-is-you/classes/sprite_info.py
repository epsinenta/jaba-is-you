from dataclasses import dataclass
from pathlib import Path
from typing import Union

from global_types import COLOR


@dataclass(unsafe_hash=True)
class SpriteInfo:
    """Необходим для грамотного хранения спрайтов в кэше"""
    path: Union[Path, str]
    have_alpha_channel: bool = True
    color: COLOR = (255, 255, 255)
