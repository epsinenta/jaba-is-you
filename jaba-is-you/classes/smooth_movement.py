import sys
import time
import traceback
from typing import Optional, Tuple
from settings import DEBUG

from utils import map_value


class SmoothMove:
    """
    Класс для плавного движения объекта и отделения математики от отрисовки
    """

    def __init__(self, start_x_pixel: int, start_y_pixel: int, x_pixel_delta: int, y_pixel_delta: int,
                 duration_seconds: float, start_time: Optional[float] = None):
        if x_pixel_delta == y_pixel_delta and y_pixel_delta == duration_seconds and duration_seconds == 0:
            if DEBUG:
                print("ERROR: Possible division by zero!!!!", file=sys.stderr)
                traceback.print_exc()
        self.start_x_pixel: int = start_x_pixel
        self.start_y_pixel: int = start_y_pixel
        self.x_pixel_delta: int = x_pixel_delta
        self.y_pixel_delta: int = y_pixel_delta
        self._duration_seconds: float = duration_seconds
        if start_time is None:
            start_time = time.time()
        self._start_time: float = start_time

    def rerun(self, duration_seconds: float):
        self._start_time = time.time()
        self._duration_seconds = duration_seconds

    @property
    def elapsed_seconds(self) -> float:
        return min(time.time() - self._start_time, self._duration_seconds)

    @property
    def done(self) -> bool:
        return self.elapsed_seconds >= self._duration_seconds

    def update_x_and_y(self) -> Tuple[int, int]:
        """
        Обновление x и y объекта.

        :returns: Кортеж с новыми x и y
        """
        elapsed_time = self.elapsed_seconds
        new_x = map_value(elapsed_time,
                          0, self._duration_seconds,
                          self.start_x_pixel, self.start_x_pixel + self.x_pixel_delta)
        new_y = map_value(elapsed_time,
                          0, self._duration_seconds,
                          self.start_y_pixel, self.start_y_pixel + self.y_pixel_delta)
        return new_x, new_y
