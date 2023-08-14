import math

import pygame

import settings
from settings import TILE, HALF_FOV, RESOLUTION, NUM_RAYS, PROJ_COEFF, TEXTURE_SCALE, SCALE, HALF_HEIGHT, DELTA_ANGLE


def mapping(xpx, ypx):
    return (xpx // TILE) * TILE, (ypx // TILE) * TILE


def raycasting(screen, player_pos, player_angle, matrix):
    start_xpx, start_ypx = player_pos
    top_left_corner_xpx, top_left_corner_ypx = mapping(start_xpx, start_ypx)
    cur_angle = player_angle - HALF_FOV
    if RESOLUTION[0] > start_xpx >= 0 and 0 <= start_ypx < RESOLUTION[1]:
        for ray in range(NUM_RAYS):
            sin_a = math.sin(cur_angle)
            cos_a = math.cos(cur_angle)
            sin_a = sin_a if sin_a else 0.000001
            cos_a = cos_a if cos_a else 0.000001
            texture_h = None
            texture_v = None
            # check_verticals
            x, delta_x = (top_left_corner_xpx + TILE,
                          1) if cos_a >= 0 else (top_left_corner_xpx, -1)
            for _ in range(0, RESOLUTION[0], TILE):
                depth_v = (x - start_xpx) / cos_a
                y_v = start_ypx + depth_v * sin_a
                tile_v = mapping(x + delta_x, y_v)
                if tile_v[0] < 0 or tile_v[0] >= RESOLUTION[0] or tile_v[1] < 0 or tile_v[1] >= RESOLUTION[1]:
                    break
                if len(matrix[int(tile_v[1] // TILE)][int(tile_v[0] // TILE)]) > 0:
                    texture_v = matrix[int(
                        tile_v[1] // TILE)][int(tile_v[0] // TILE)][0].animation.current_sprite
                    break
                x += delta_x * TILE
            # check_horizontals
            y, delta_y = (top_left_corner_ypx + TILE,
                          1) if sin_a >= 0 else (top_left_corner_ypx, -1)
            for _ in range(0, RESOLUTION[1], TILE):
                depth_h = (y - start_ypx) / sin_a
                x_h = start_xpx + depth_h * cos_a
                tile_h = mapping(x_h, y + delta_y)
                if tile_h[0] < 0 or tile_h[0] >= RESOLUTION[0] or tile_h[1] < 0 or tile_h[1] >= RESOLUTION[1]:
                    break
                if len(matrix[int(tile_h[1] // TILE)][int(tile_h[0] // TILE)]) > 0:
                    texture_h = matrix[int(
                        tile_h[1] // TILE)][int(tile_h[0] // TILE)][0].animation.current_sprite
                    break
                y += delta_y * TILE

            # projection
            depth, offset, texture = (depth_v, y_v, texture_v) if depth_v < depth_h else (
                depth_h, x_h, texture_h)
            if texture is not None:
                offset = int(offset) % TILE
                depth *= math.cos(player_angle - cur_angle)
                depth = max(depth, 0.00001)
                proj_height = min(int(PROJ_COEFF / depth), RESOLUTION[1])
                wall_column = texture.subsurface(
                    (TILE - offset - 1) * TEXTURE_SCALE, 0, TEXTURE_SCALE, 50)
                wall_column = pygame.transform.scale(
                    wall_column, (SCALE * settings.WINDOW_SCALE, proj_height * settings.WINDOW_SCALE))
                screen.blit(wall_column, (ray * SCALE * settings.WINDOW_SCALE,
                            (HALF_HEIGHT - proj_height // 2) * settings.WINDOW_SCALE))

            cur_angle += DELTA_ANGLE
