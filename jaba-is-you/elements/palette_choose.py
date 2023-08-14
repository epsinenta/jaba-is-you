from typing import List, Optional, TYPE_CHECKING

import pygame

import settings
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.palette import Palette
from classes.state import State
from elements.global_classes import palette_manager, language_manager
from global_types import SURFACE

if TYPE_CHECKING:
    from elements.editor import Editor


class PaletteChoose(GameStrategy):
    def __init__(self, editor: "Editor", screen: SURFACE):
        super().__init__(screen)
        self.editor: "Editor" = editor
        font = pygame.font.SysFont("Arial", int(
            72 * 2.5 * settings.WINDOW_SCALE))
        self._choose_palette_text = font.render(
            f"{language_manager['Choose a palette']}:", True, (255, 255, 255))
        super().__init__(screen)

    def _process_palette(self, x_pixel_offset, y_pixel_offset, events: List[pygame.event.Event]) -> Optional[Palette]:
        """
        Отрисовка и обработка палитр

        :param x_pixel_offset: Отступ по оси x
        :param y_pixel_offset: Отступ по оси y
        :return: None, или палитру на которую нажали
        """
        distance_between_palettes = round(5 * settings.WINDOW_SCALE)
        pixel_size = round(35 * settings.WINDOW_SCALE)
        for palette in palette_manager.palettes:
            length_of_palette_pixels_abscissa = len(palette.pixels[-1])
            length_of_palette_pixels_ordinate = len(palette.pixels)

            palette_surface = pygame.surface.Surface((pixel_size * length_of_palette_pixels_abscissa,
                                                      pixel_size * length_of_palette_pixels_ordinate))
            palette.draw(palette_surface, pixel_size, 0, 0)
            if pygame.rect.Rect(
                    x_pixel_offset,
                    y_pixel_offset,
                    pixel_size * length_of_palette_pixels_abscissa,
                    pixel_size * length_of_palette_pixels_ordinate
            ).collidepoint(pygame.mouse.get_pos()):
                color_mask = pygame.surface.Surface((pixel_size * length_of_palette_pixels_abscissa,
                                                     pixel_size * length_of_palette_pixels_ordinate))
                color_mask.fill("lightgray")
                palette_surface.blit(color_mask, (0, 0),
                                     special_flags=pygame.BLEND_MULT)
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        return palette
            self.screen.blit(palette_surface, (x_pixel_offset, y_pixel_offset))

            x_pixel_offset += length_of_palette_pixels_abscissa * \
                pixel_size + distance_between_palettes
            if x_pixel_offset + length_of_palette_pixels_abscissa * pixel_size > self.screen.get_width():
                y_pixel_offset += pixel_size * \
                    length_of_palette_pixels_ordinate + distance_between_palettes
                x_pixel_offset = 0
        return None

    def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        state = None
        self.screen.fill('black')

        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                state = State(GameState.BACK)

        self.screen.blit(self._choose_palette_text, (0, 0))
        palette = self._process_palette(
            0, self._choose_palette_text.get_height(), events)
        pygame.display.flip()

        if palette is not None:
            self.editor.current_palette = palette
            self.editor.define_border_and_scale()
            state = State(GameState.BACK)
            if settings.DEBUG:
                print(f"choose: {self.editor.current_palette.name}")

            pygame.event.set_allowed(None)

        return state

    def on_init(self):
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
        if settings.DEBUG:
            print("QUIT and KEYDOWN")
