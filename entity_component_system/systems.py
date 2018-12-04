from typing import List, Iterable, Callable
import pygame
from entity_component_system.component import Component, GraphicsComponent, TextComponent, VelocityComponent, \
    HorizontalOrientationComponent, AnimationCycleComponent, LifeTimeComponent, LEFT_DIRECTION, RIGHT_DIRECTION
from entity_component_system.entities_manager import EntitiesManager, get_component_of_entity


NO_COLLISIONS = -1


def erase_system(screen: pygame.Surface, background: pygame.Surface, graphics_components: Iterable[GraphicsComponent]) \
        -> List[pygame.Rect]:
    dirty_rects = list()
    for graphics_compo in graphics_components:
        dirty_rects.append(screen.blit(background, graphics_compo.rect, graphics_compo.rect))
    return dirty_rects


def draw_system(screen: pygame.Surface, graphics_components: Iterable[GraphicsComponent]) -> List[pygame.Rect]:
    dirty_rects = list()
    for graphics_compo in graphics_components:
        dirty_rects.append(screen.blit(graphics_compo.surface, graphics_compo.rect))
    return dirty_rects


def rotate_animation_cycle_system(entities_composed_of_graphics_and_ani_cycle_list: Iterable[List[Component]]) -> None:
    for entity in entities_composed_of_graphics_and_ani_cycle_list:
        graphics_compo = get_component_of_entity(entity, GraphicsComponent)
        ani_cycle_compo = get_component_of_entity(entity, AnimationCycleComponent)
        for additional_surface in ani_cycle_compo.surfaces:
            if graphics_compo.surface == additional_surface:
                ani_cycle_compo.ani_cycle_count += 1
                idx = ani_cycle_compo.ani_cycle_count // ani_cycle_compo.interval_len % len(ani_cycle_compo.surfaces)
                graphics_compo.surface = ani_cycle_compo.surfaces[idx]
                break


def rewrite_text_system(entity_composed_of_graphics_and_text_components: List[Component], new_text: str) -> None:
    graphics_compo = get_component_of_entity(entity_composed_of_graphics_and_text_components, GraphicsComponent)
    text_compo = get_component_of_entity(entity_composed_of_graphics_and_text_components, TextComponent)
    text_compo.text = new_text
    graphics_compo.surface = text_compo.font.render(text_compo.text, False, text_compo.color)


def move_horizontally_oriented_entity_system(entity: List[Component], curr_x_direction: int, right_edge: int) \
        -> None:
    graphics_compo = get_component_of_entity(entity, GraphicsComponent)
    velocity_compo = get_component_of_entity(entity, VelocityComponent)
    hori_ori_compo = get_component_of_entity(entity, HorizontalOrientationComponent)

    if hori_ori_compo.last_horizontal_direction != curr_x_direction:
        if curr_x_direction == LEFT_DIRECTION:
            graphics_compo.surface = hori_ori_compo.left_oriented_surface
            hori_ori_compo.last_horizontal_direction = LEFT_DIRECTION
        elif curr_x_direction == RIGHT_DIRECTION:
            graphics_compo.surface = hori_ori_compo.right_oriented_surface
            hori_ori_compo.last_horizontal_direction = RIGHT_DIRECTION

    graphics_compo.rect.move_ip(velocity_compo.x_velocity * curr_x_direction, 0)
    graphics_compo.rect.left = max(graphics_compo.rect.left, 0)
    graphics_compo.rect.right = min(graphics_compo.rect.right, right_edge)


def collision_detection_system(entity: List[Component], other_entities: Iterable[List[Component]]) -> int:
    entity_rect = get_component_of_entity(entity, GraphicsComponent).rect
    other_entities_rects = list()
    for other_entity in other_entities:
        other_entity_graphics_compo = get_component_of_entity(other_entity, GraphicsComponent)
        other_entities_rects.append(other_entity_graphics_compo.rect)
    return entity_rect.collidelist(other_entities_rects)


def collision_detection_with_handling_system(entity: List[Component], other_entities: Iterable[List[Component]],
                                             entities_manager: EntitiesManager, handler: Callable[..., None], *args,
                                             **kwargs) -> None:
    entity_rect = get_component_of_entity(entity, GraphicsComponent).rect
    other_entities_rects = list()
    for other_entity in other_entities:
        other_entity_graphics_compo = get_component_of_entity(other_entity, GraphicsComponent)
        other_entities_rects.append(other_entity_graphics_compo.rect)
    collided_entity_idx = entity_rect.collidelist(other_entities_rects)
    if collided_entity_idx != NO_COLLISIONS:
        handler(other_entities, collided_entity_idx, entities_manager, *args, *kwargs)


def decrease_lifetime_system(entities_composed_of_lifetime_compo: Iterable[List[Component]],
                             entities_manager: EntitiesManager, entities_type_id: int) -> None:
    for entity in entities_composed_of_lifetime_compo:
        life_time_compo = get_component_of_entity(entity, LifeTimeComponent)
        life_time_compo.life_time -= 1
        if life_time_compo.life_time == 0:
            entities_manager.remove_entity_by_type_id_and_entity_id(entities_type_id, entity[0].entity_id)
