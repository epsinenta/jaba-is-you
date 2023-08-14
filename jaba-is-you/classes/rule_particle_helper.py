import time
from random import choice
from typing import Optional, TYPE_CHECKING, Sequence, Set, List, Callable

from classes.objects import Object
from classes.particle import Particle, ParticleStrategy
from classes.text_rule import TextRule
from elements.global_classes import sprite_manager
from global_types import COLOR

if TYPE_CHECKING:
    from elements.play_level import PlayLevel


class ParticleMover:
    """
    Класс двигающий партиклы
    """

    def __init__(self, x_offset: Sequence[int], y_offset: Sequence[int], size: Sequence[int],
                 max_rotation: Sequence[int], wait_delay: float, duration: float, particle_sprite_name: str,
                 count: Optional[Sequence[int]] = None, sprite_colors: Optional[Sequence[COLOR]] = None):
        """
        Конструктор класса

        :param x_offset: Диапазон чисел в котором случайно будет выбираться отступ для партикла по оси x
        :param y_offset: Диапазон чисел в котором случайно будет выбираться отступ для партикла по оси y
        :param size: Диапазон чисел в котором случайно будет выбираться размер для партикла
        :param max_rotation: Диапазон чисел в котором случайно будет выбираться градус поворота в конце анимации
        :param wait_delay:
            Число, обозначающее задержку между созданием партиклов, отрицательное если всегда вызывается вручную
        :param duration: Длительность партикла
        :param count: Диапазон чисел в котором случайно будет выбираться количество частиц за раз
        :param particle_sprite_name: Название спрайта для партикла
        """
        # Настройки частиц
        self.count = count if count is not None else range(1, 4)
        self.wait_delay: float = wait_delay
        self.duration: float = duration
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.size = size
        self.max_rotation = max_rotation
        self.particle_sprite_name = particle_sprite_name
        self.sprite_colors: Optional[Sequence[COLOR]] = sprite_colors
        # Ужасная подноготная TODO: которую желательно сделать отдельным классом
        self._level_processor: Optional["PlayLevel"] = None
        self._rule_objects: Set[Object] = set()
        self._timer: Optional[float] = None

    def for_rule_objects(self, func: Callable):
        for rule in self._rule_objects:
            func(rule)

    def update_on_apply(self, level_processor: "PlayLevel", rule_object: Object, color: Optional[str] = None,
                        force_not_start: bool = False):
        """
        Инкапсуляция :attr:`~.ParticleMover.rule_object` и :attr:`~.ParticleMover.level_processor`
        То есть устанавливает их.

        :param force_not_start:
            Костыль. Если True, не вызывает :meth:`~.ParticleMover.start`.
            Ставьте True, только если вы осознаёте что вы делаете.
        :param level_processor: Обработчик уровня
        :param rule_object: Объект к которому применяются партиклы
        :param color: Объект из которого необходимо брать цвет
        :return: Ничего
        """
        if level_processor != self._level_processor:
            self._rule_objects.clear()
        self._level_processor = level_processor
        have_rule_object = False
        for rule in self._rule_objects:
            if repr(rule) == repr(rule_object):
                have_rule_object = True
                break
        if not have_rule_object:
            self._rule_objects.clear()
            self._rule_objects.add(rule_object)
        if color is not None:
            palette_pixel_position = sprite_manager.default_colors[color]
            self.sprite_colors = [self._level_processor.current_palette.pixels[
                palette_pixel_position[1]][palette_pixel_position[0]]]
        if not self.started and not force_not_start:
            self.start()

    def update_on_rules_changed(self, new_rules: List[TextRule], rule_name: str, force_not_start: bool = False):
        need_to_stop = True
        for rule in new_rules:
            rule_end = f' is {rule_name}'
            if rule_end in rule.text_rule and rule.text_rule[:rule.text_rule.index(rule_end)] in \
                    [i.name for i in self._rule_objects]:
                need_to_stop = False
        if self.started and need_to_stop:
            self.stop()
            return False
        return True

    def stop(self):
        """
        Посылает запрос на остановку изменения частиц

        :return: Ничего
        """
        if not self.started:
            return
        self._timer = None
        self._rule_objects.clear()

    def start(self):
        """
        Запускает изменение частиц
        :return: Ничего
        """
        if self.started:
            return
        self._timer = time.time()

    @property
    def started(self) -> bool:
        """
        .. getter: Возвращает bool, означающий запущен ли поток или нет

        .. setter:
            Нету.
            Используйте :meth:`~.ParticleMover.start` для запуска
            или :meth:`~.ParticleMover.stop` для остановки
        """
        return self._timer is not None

    @property
    def rule_objects(self) -> Set[Object]:
        return self._rule_objects

    def _work_one_particle(self, rule_object: Object):
        if self._level_processor is None:
            raise RuntimeError("self._level_processor is not initialized")
        for _ in range(choice(self.count)):
            x_offset = choice(self.x_offset)
            y_offset = choice(self.y_offset)
            size = choice(self.size)
            max_rotation = choice(self.max_rotation)
            color: COLOR
            if self.sprite_colors is None:
                palette_pixel_position = sprite_manager.default_colors[rule_object.name]
                color = self._level_processor.current_palette.pixels[
                    palette_pixel_position[1]][
                    palette_pixel_position[0]]
            else:
                color = choice(self.sprite_colors)
            self._level_processor.particles.append(Particle(self.particle_sprite_name, ParticleStrategy(
                (rule_object.xpx, rule_object.xpx + x_offset),
                (rule_object.ypx, rule_object.ypx + y_offset),
                (size, size),
                (0, max_rotation), 10,
                self.duration,
                randomize_start_values=True
            ), color))

    def every_frame(self, force_draw: bool = False):
        if not force_draw and (self._timer is None or self.wait_delay < 0 or (time.time() - self._timer) < self.wait_delay):
            return
        for rule_object in self._rule_objects:
            self._work_one_particle(rule_object)
        self._timer = time.time()
