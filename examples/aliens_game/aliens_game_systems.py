from typing import List, Callable
import pygame
from entity_component_system.component import Component, GraphicsComponent, VelocityComponent
from entity_component_system.entities_manager import EntitiesManager, get_component_of_entity
from entity_component_system.systems import rewrite_text_system, NO_COLLISIONS


def move_aliens_system(aliens_list: List[List[Component]], right_edge: int) -> None:
    for alien in aliens_list:
        graphics_compo = get_component_of_entity(alien, GraphicsComponent)
        velocity_compo = get_component_of_entity(alien, VelocityComponent)
        graphics_compo.rect.move_ip(velocity_compo.x_velocity, velocity_compo.y_velocity)
        if graphics_compo.rect.left > right_edge:
            graphics_compo.rect.left = right_edge
        elif graphics_compo.rect.right < 0:
            graphics_compo.rect.right = 0
        if graphics_compo.rect.left == right_edge or graphics_compo.rect.right == 0:
            velocity_compo.x_velocity *= -1
            graphics_compo.rect.top = graphics_compo.rect.bottom + 1


def move_shots_system(shots_list: List[List[Component]], entities_manager: EntitiesManager, shot_type_id: int) -> None:
    for shot in shots_list:
        graphics_compo = get_component_of_entity(shot, GraphicsComponent)
        velocity_compo = get_component_of_entity(shot, VelocityComponent)
        graphics_compo.rect.move_ip(velocity_compo.x_velocity, velocity_compo.y_velocity)
        if graphics_compo.rect.bottom < 0:
            entities_manager.remove_entity_by_type_id_and_entity_id(shot_type_id, graphics_compo.entity_id)


def move_bombs_system(bombs_list: List[List[Component]], bottom_edge: int, entities_manager: EntitiesManager,
                      bomb_type_id: int, explosions_factory: Callable[[int, int], int]) -> None:
    for bomb in bombs_list:
        graphics_compo = get_component_of_entity(bomb, GraphicsComponent)
        velocity_compo = get_component_of_entity(bomb, VelocityComponent)
        graphics_compo.rect.move_ip(velocity_compo.x_velocity, velocity_compo.y_velocity)
        if bottom_edge < graphics_compo.rect.bottom:
            explosions_factory(graphics_compo.rect.center[0], graphics_compo.rect.center[1])
            entities_manager.remove_entity_by_type_id_and_entity_id(bomb_type_id, graphics_compo.entity_id)


def handle_afv_collision(collided_entities: List[List[Component]], collided_entity_idx: int,
                         entities_manager: EntitiesManager, alien_type_id: int, afv_rect: pygame.Rect, lives_id: int,
                         curr_life: List[int], life_penalty: int, explosion_factory: Callable[[int, int], int],
                         screen: pygame.Surface, background: pygame.Surface, dirty_rects: List[pygame.Rect]) -> None:
    curr_life[0] -= life_penalty
    rewrite_text_system(entities_manager.get_entity(lives_id), "Lives: {}".format(curr_life[0]), screen, background,
                        dirty_rects)
    explosion_factory(afv_rect.center[0], afv_rect.center[1])
    collided_entity_id = collided_entities[collided_entity_idx][0].entity_id
    if entities_manager.get_entity_type_id(collided_entity_id) == alien_type_id:
        alien_rect = get_component_of_entity(collided_entities[collided_entity_idx], GraphicsComponent).rect
        explosion_factory(alien_rect.center[0], alien_rect.center[1])


def detect_shot_at_aliens_system(shots_list: List[List[Component]], aliens_list: List[List[Component]],
                                 entities_manager: EntitiesManager, score_id: int, curr_score: List[int],
                                 alien_hit_reward: int, explosions_factory: Callable[[int, int], int],
                                 screen: pygame.Surface, background: pygame.Surface, dirty_rects: List[pygame.Rect]) \
        -> None:
    aliens_rects = list()
    aliens_ids = list()
    for alien in aliens_list:
        alien_graphics_compo = get_component_of_entity(alien, GraphicsComponent)
        aliens_rects.append(alien_graphics_compo.rect)
        aliens_ids.append(alien_graphics_compo.entity_id)

    for shot in shots_list:
        shot_graphics_compo = get_component_of_entity(shot, GraphicsComponent)
        hit = shot_graphics_compo.rect.collidelist(aliens_rects)
        if hit != NO_COLLISIONS:
            alien = entities_manager.get_entity(aliens_ids[hit])
            alien_rect = get_component_of_entity(alien, GraphicsComponent).rect
            explosions_factory(alien_rect.center[0], alien_rect.center[1])
            curr_score[0] += alien_hit_reward
            rewrite_text_system(entities_manager.get_entity(score_id), "Score: {}".format(curr_score[0]), screen,
                                background, dirty_rects)
            entities_manager.remove_entity(alien)
            entities_manager.remove_entity(shot)
