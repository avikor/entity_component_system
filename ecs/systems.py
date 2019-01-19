from typing import Iterable, List, Callable, Dict
import pygame
from ecs.component import GraphicComponent, LEFT_DIRECTION, RIGHT_DIRECTION
from ecs.entities_manager import Entity, EntitiesManager


NO_COLLISIONS = -1


def erase_system(screen: pygame.Surface, background: pygame.Surface, graphic_components: Iterable[GraphicComponent],
                 dirty_rects: List[pygame.Rect]) -> None:
    for graphic_compo in graphic_components:
        dirty_rects.append(screen.blit(background, graphic_compo.rect, graphic_compo.rect))


def draw_system(screen: pygame.Surface, graphic_components: Iterable[GraphicComponent],
                dirty_rects: List[pygame.Rect]) -> None:
    for graphic_compo in graphic_components:
        dirty_rects.append(screen.blit(graphic_compo.surface, graphic_compo.rect))


def rotate_animation_cycle_system(entities_composed_of_graphic_and_ani_cycle: Iterable[Entity]) -> None:
    for entity in entities_composed_of_graphic_and_ani_cycle:
        ani_cycle_compo = entity["AnimationCycleComponent"]
        graphic_compo = entity["GraphicComponent"]
        for additional_surface in ani_cycle_compo.surfaces:
            if graphic_compo.surface == additional_surface:
                ani_cycle_compo.ani_cycle_count += 1
                idx = (ani_cycle_compo.ani_cycle_count // ani_cycle_compo.interval_len) % len(ani_cycle_compo.surfaces)
                graphic_compo.surface = ani_cycle_compo.surfaces[idx]
                break


def rewrite_text_system(screen: pygame.Surface, background: pygame.Surface, dirty_rects: List[pygame.Rect],
                        entity_composed_of_graphic_and_text_components: Entity, new_text: str) -> None:
    graphic_compo = entity_composed_of_graphic_and_text_components["GraphicComponent"]
    text_compo = entity_composed_of_graphic_and_text_components["TextComponent"]
    text_compo.text = new_text
    dirty_rects.append(screen.blit(background, graphic_compo.rect, graphic_compo.rect))
    graphic_compo.surface = text_compo.font.render(text_compo.text, False, text_compo.color)
    old_rect_x, old_rect_y = graphic_compo.rect.x, graphic_compo.rect.y
    graphic_compo.rect = graphic_compo.surface.get_rect()
    graphic_compo.rect.move_ip(old_rect_x, old_rect_y)
    dirty_rects.append(screen.blit(graphic_compo.surface, graphic_compo.rect))


def move_system(entities: Iterable[Entity], off_bounds_handler: Callable[[Entity], None], curr_x_direction: int = 0) \
        -> None:
    for entity in entities:
        graphic_compo = entity["GraphicComponent"]
        velocity_compo = entity["VelocityComponent"]
        if "HorizontalOrientationComponent" in entity and curr_x_direction != 0:
            hori_ori_compo = entity["HorizontalOrientationComponent"]
            if hori_ori_compo.last_horizontal_direction != curr_x_direction:
                if curr_x_direction == LEFT_DIRECTION:
                    graphic_compo.surface = hori_ori_compo.left_oriented_surface
                    hori_ori_compo.last_horizontal_direction = LEFT_DIRECTION
                elif curr_x_direction == RIGHT_DIRECTION:
                    graphic_compo.surface = hori_ori_compo.right_oriented_surface
                    hori_ori_compo.last_horizontal_direction = RIGHT_DIRECTION
            graphic_compo.rect.move_ip(velocity_compo.x_velocity * curr_x_direction, velocity_compo.y_velocity)
        else:
            graphic_compo.rect.move_ip(velocity_compo.x_velocity, velocity_compo.y_velocity)
        off_bounds_handler(entity)


def collision_detection_system(entity: Entity, other_entities: Iterable[Entity]) -> int:
    entity_rect = entity["GraphicComponent"].rect
    other_entities_rects = list()
    for other_entity in other_entities:
        other_entity_graphic_compo = other_entity["GraphicComponent"]
        other_entities_rects.append(other_entity_graphic_compo.rect)
    return entity_rect.collidelist(other_entities_rects)


def collision_detection_with_handling_system(entity: Entity, other_entities: Iterable[Entity],
                                             entities_manager: EntitiesManager,
                                             handler: Callable[[Iterable[Entity], int, EntitiesManager],
                                                               None]) -> None:
    entity_rect = entity["GraphicComponent"].rect
    other_entities_rects = list()
    for other_entity in other_entities:
        other_entity_graphic_compo = other_entity["GraphicComponent"]
        other_entities_rects.append(other_entity_graphic_compo.rect)
    collided_entity_idx = entity_rect.collidelist(other_entities_rects)
    if collided_entity_idx != NO_COLLISIONS:
        handler(other_entities, collided_entity_idx, entities_manager)


def lists_collision_detection_system(entities: List[Entity],
                                     other_entities: List[Entity]) -> Dict[int, List[int]]:
    """  This system receives two lists of entities, and outputs a dictionary whose keys are indices of entities of the
         first list, and whose values are indices of the entities of the second list with which the entity of the
         first list collides with. """
    other_entities_rects = list()
    for other_entity in other_entities:
        other_entities_rects.append(other_entity["GraphicComponent"].rect)

    collisions = dict()
    for i in range(len(entities)):
        entity_rect = entities[i]["GraphicComponent"].rect
        collision_indices = entity_rect.collidelistall(other_entities_rects)
        if collision_indices:
            collisions[i] = collision_indices
    return collisions


def lists_collision_detection_with_handling_system(entities: List[Entity],
                                                   other_entities: List[Entity],
                                                   entities_manager: EntitiesManager,
                                                   handler: Callable[[Entity, List[Entity],
                                                                      List[int], EntitiesManager], None]) -> None:
    """  This system receives two lists of entities, and calls the collision handler whenever an entity from the first
         list collided with entities from the second list. """
    other_entities_rects = list()
    for other_entity in other_entities:
        other_entities_rects.append(other_entity["GraphicComponent"].rect)

    for entity in entities:
        entity_rect = entity["GraphicComponent"].rect
        collision_indices = entity_rect.collidelistall(other_entities_rects)
        if collision_indices:
            handler(entity, other_entities, collision_indices, entities_manager)


def decrease_lifetime_system(entities_composed_of_lifetime_compo: Iterable[Entity],
                             entities_manager: EntitiesManager) -> None:
    for entity in entities_composed_of_lifetime_compo:
        life_time_compo = entity["LifeTimeComponent"]
        life_time_compo.life_time -= 1
        if life_time_compo.life_time == 0:
            entities_manager.unregister_and_discharge_entity_from_all_groups(entity)
