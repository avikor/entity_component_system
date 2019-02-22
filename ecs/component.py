from typing import Tuple
import pygame


LEFT_DIRECTION = -1
RIGHT_DIRECTION = 1


class GraphicComponent:
    def __init__(self, surface: pygame.Surface, initial_x: int, initial_y: int) -> None:
        self.surface = surface
        self.rect = self.surface.get_rect()
        self.rect.move_ip(initial_x, initial_y)


class AnimationCycleComponent:
    def __init__(self, surfaces: Tuple[pygame.Surface, ...], interval_length: int) -> None:
        self.surfaces = surfaces
        self.interval_len = interval_length
        self.ani_cycle_count = 0


class TextComponent:
    def __init__(self, text: str, size: int, color: str):
        self.text = text
        self.size = size
        self.color = pygame.color.Color(color)
        self.font = pygame.font.Font(None, self.size)


class VelocityComponent:
    def __init__(self, x_velocity: int, y_velocity: int) -> None:
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity


class HorizontalOrientationComponent:
    def __init__(self, left_oriented_surface: pygame.Surface = None, right_oriented_surface: pygame.Surface = None,
                 last_horizontal_direction: int = LEFT_DIRECTION) -> None:
        if left_oriented_surface is None and right_oriented_surface is None:
            raise ValueError()
        self.left_oriented_surface = left_oriented_surface
        self.right_oriented_surface = right_oriented_surface
        self.last_horizontal_direction = last_horizontal_direction


class AudioComponent:
    def __init__(self, sound: pygame.mixer.Sound) -> None:
        self.sound = sound


class LifeTimeComponent:
    def __init__(self, life_time: int) -> None:
        self.life_time = life_time
