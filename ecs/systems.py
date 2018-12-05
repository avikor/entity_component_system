from typing import List, Iterable, Callable, Dict
import pygame
from ecs.component import Component, GraphicComponent, TextComponent, VelocityComponent, \
    HorizontalOrientationComponent, AnimationCycleComponent, LifeTimeComponent, LEFT_DIRECTION, RIGHT_DIRECTION
from ecs.entities_manager import EntitiesManager, get_component_of_entity


NO_COLLISIONS = -1


def erase_system(screen: pygame.Surface, background: pygame.Surface, graphic_components: Iterable[GraphicComponent],
                 dirty_rects: List[pygame.Rect]) -> None:
    for graphic_compo in graphic_components:
        dirty_rects.append(screen.blit(background, graphic_compo.rect, graphic_compo.rect))


def draw_system(screen: pygame.Surface, graphic_components: Iterable[GraphicComponent],
                dirty_rects: List[pygame.Rect]) -> None:
    for graphic_compo in graphic_components:
        dirty_rects.append(screen.blit(graphic_compo.surface, graphic_compo.rect))


def rotate_animation_cycle_system(entities_composed_of_graphic_and_ani_cycle_list: Iterable[List[Component]]) -> None:
    for entity in entities_composed_of_graphic_and_ani_cycle_list:
        graphic_compo = get_component_of_entity(entity, GraphicComponent)
        ani_cycle_compo = get_component_of_entity(entity, AnimationCycleComponent)
        for additional_surface in ani_cycle_compo.surfaces:
            if graphic_compo.surface == additional_surface:
                ani_cycle_compo.ani_cycle_count += 1
                idx = ani_cycle_compo.ani_cycle_count // ani_cycle_compo.interval_len % len(ani_cycle_compo.surfaces)
                graphic_compo.surface = ani_cycle_compo.surfaces[idx]
                break


def rewrite_text_system(entity_composed_of_graphic_and_text_components: List[Component], new_text: str,
                        screen: pygame.Surface, background: pygame.Surface, dirty_rects: List[pygame.Rect]) -> None:
    graphic_compo = get_component_of_entity(entity_composed_of_graphic_and_text_components, GraphicComponent)
    text_compo = get_component_of_entity(entity_composed_of_graphic_and_text_components, TextComponent)
    text_compo.text = new_text
    dirty_rects.append(screen.blit(background, graphic_compo.rect, graphic_compo.rect))
    graphic_compo.surface = text_compo.font.render(text_compo.text, False, text_compo.color)
    old_rect = graphic_compo.rect
    graphic_compo.rect = graphic_compo.surface.get_rect()
    graphic_compo.rect.move_ip(old_rect.x, old_rect.y)
    dirty_rects.append(screen.blit(graphic_compo.surface, graphic_compo.rect))


def move_system(entities: Iterable[List[Component]],
                off_bounds_handler: Callable[[GraphicComponent, VelocityComponent], None]):
    for entity in entities:
        graphic_compo = get_component_of_entity(entity, GraphicComponent)
        velocity_compo = get_component_of_entity(entity, VelocityComponent)
        graphic_compo.rect.move_ip(velocity_compo.x_velocity, velocity_compo.y_velocity)
        off_bounds_handler(graphic_compo, velocity_compo)


def move_screen_bounded_horizontally_oriented_entity_system(entity: List[Component], curr_x_direction: int,
                                                            right_edge: int) -> None:
    graphic_compo = get_component_of_entity(entity, GraphicComponent)
    velocity_compo = get_component_of_entity(entity, VelocityComponent)
    hori_ori_compo = get_component_of_entity(entity, HorizontalOrientationComponent)

    if hori_ori_compo.last_horizontal_direction != curr_x_direction:
        if curr_x_direction == LEFT_DIRECTION:
            graphic_compo.surface = hori_ori_compo.left_oriented_surface
            hori_ori_compo.last_horizontal_direction = LEFT_DIRECTION
        elif curr_x_direction == RIGHT_DIRECTION:
            graphic_compo.surface = hori_ori_compo.right_oriented_surface
            hori_ori_compo.last_horizontal_direction = RIGHT_DIRECTION

    graphic_compo.rect.move_ip(velocity_compo.x_velocity * curr_x_direction, 0)
    graphic_compo.rect.left = max(graphic_compo.rect.left, 0)
    graphic_compo.rect.right = min(graphic_compo.rect.right, right_edge)


def collision_detection_system(entity: List[Component], other_entities: Iterable[List[Component]]) -> int:
    entity_rect = get_component_of_entity(entity, GraphicComponent).rect
    other_entities_rects = list()
    for other_entity in other_entities:
        other_entity_graphic_compo = get_component_of_entity(other_entity, GraphicComponent)
        other_entities_rects.append(other_entity_graphic_compo.rect)
    return entity_rect.collidelist(other_entities_rects)


def collision_detection_with_handling_system(entity: List[Component], other_entities: Iterable[List[Component]],
                                             entities_manager: EntitiesManager,
                                             handler: Callable[[Iterable[List[Component]], int, EntitiesManager],
                                                               None]) -> None:
    entity_rect = get_component_of_entity(entity, GraphicComponent).rect
    other_entities_rects = list()
    for other_entity in other_entities:
        other_entity_graphic_compo = get_component_of_entity(other_entity, GraphicComponent)
        other_entities_rects.append(other_entity_graphic_compo.rect)
    collided_entity_idx = entity_rect.collidelist(other_entities_rects)
    if collided_entity_idx != NO_COLLISIONS:
        handler(other_entities, collided_entity_idx, entities_manager)


def lists_collision_detection_system(entities: List[List[Component]],
                                     other_entities: List[List[Component]]) -> Dict[int, List[int]]:
    """  This system receives two lists of entities, and outputs a dictionary whose keys are indices of entities of the
         first list, and whose values are indices of the entities of the second list with which the entity of the
         first list collides with. """
    other_entities_rects = list()
    for other_entity in other_entities:
        other_entities_rects.append(get_component_of_entity(other_entity, GraphicComponent).rect)

    collisions = dict()
    for i in range(len(entities)):
        entity_rect = get_component_of_entity(entities[i], GraphicComponent).rect
        collision_indices = entity_rect.collidelistall(other_entities_rects)
        if collision_indices:
            collisions[i] = collision_indices
    return collisions


def lists_collision_detection_with_handling_system(entities: List[List[Component]],
                                                   other_entities: List[List[Component]],
                                                   entities_manager: EntitiesManager, handler: Callable) -> None:
    other_entities_rects = list()
    for other_entity in other_entities:
        other_entities_rects.append(get_component_of_entity(other_entity, GraphicComponent).rect)

    for entity in entities:
        entity_rect = get_component_of_entity(entity, GraphicComponent).rect
        collision_indices = entity_rect.collidelistall(other_entities_rects)
        if collision_indices:
            handler(entity, other_entities, collision_indices, entities_manager)


def decrease_lifetime_system(entities_composed_of_lifetime_compo: Iterable[List[Component]],
                             entities_manager: EntitiesManager, entities_type_id: int) -> None:
    for entity in entities_composed_of_lifetime_compo:
        life_time_compo = get_component_of_entity(entity, LifeTimeComponent)
        life_time_compo.life_time -= 1
        if life_time_compo.life_time == 0:
            entities_manager.remove_entity_by_type_id_and_entity_id(entities_type_id, entity[0].entity_id)
