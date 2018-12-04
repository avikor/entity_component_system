from abc import ABCMeta
from typing import Tuple
import pygame


LEFT_DIRECTION = -1
RIGHT_DIRECTION = 1


class Component(metaclass=ABCMeta):
    def __init__(self):
        self.entity_id = -1


class GraphicsComponent(Component):
    def __init__(self, surface: pygame.Surface, initial_x: int, initial_y: int) -> None:
        super(GraphicsComponent, self).__init__()
        self.surface = surface
        self.rect = self.surface.get_rect()
        self.rect.move_ip(initial_x, initial_y)


class AnimationCycleComponent(Component):
    def __init__(self, surfaces: Tuple[pygame.Surface, ...], interval_length: int) -> None:
        super(AnimationCycleComponent, self).__init__()
        self.surfaces = surfaces
        self.interval_len = interval_length
        self.ani_cycle_count = 0


class TextComponent(Component):
    def __init__(self, text: str, size: int, color: str):
        super(TextComponent, self).__init__()
        self.text = text
        self.size = size
        self.color = pygame.color.Color(color)
        self.font = pygame.font.Font(None, self.size)


class VelocityComponent(Component):
    def __init__(self, x_velocity: int, y_velocity: int) -> None:
        super(VelocityComponent, self).__init__()
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity


class HorizontalOrientationComponent(Component):
    def __init__(self, left_oriented_surface: pygame.Surface = None, right_oriented_surface: pygame.Surface = None,
                 last_horizontal_direction: int = LEFT_DIRECTION) -> None:
        if left_oriented_surface is None and right_oriented_surface is None:
            raise ValueError()
        super(HorizontalOrientationComponent, self).__init__()
        self.left_oriented_surface = left_oriented_surface
        self.right_oriented_surface = right_oriented_surface
        self.last_horizontal_direction = last_horizontal_direction


class AudioComponent(Component):
    def __init__(self, sound: pygame.mixer.Sound) -> None:
        super(AudioComponent, self).__init__()
        self.sound = sound


class LifeTimeComponent(Component):
    def __init__(self, life_time: int) -> None:
        super(LifeTimeComponent, self).__init__()
        self.life_time = life_time
