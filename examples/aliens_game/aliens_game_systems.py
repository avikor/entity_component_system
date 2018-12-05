from typing import List, Callable, Iterable
import pygame
import ecs


def move_aliens_system(aliens_list: List[List[ecs.Component]], right_edge: int) -> None:
    def aliens_off_bounds_handler(graphics_compo: ecs.GraphicsComponent, velocity_compo: ecs.VelocityComponent) -> None:
        if graphics_compo.rect.left > right_edge:
            graphics_compo.rect.left = right_edge
        elif graphics_compo.rect.right < 0:
            graphics_compo.rect.right = 0
        if graphics_compo.rect.left == right_edge or graphics_compo.rect.right == 0:
            velocity_compo.x_velocity *= -1
            graphics_compo.rect.top = graphics_compo.rect.bottom + 1

    ecs.move_system(aliens_list, aliens_off_bounds_handler)


def move_shots_system(shots_list: List[List[ecs.Component]], entities_manager: ecs.EntitiesManager, shot_type_id: int) \
        -> None:
    def shots_off_bounds_handler(graphics_compo: ecs.GraphicsComponent, velocity_compo: ecs.VelocityComponent) -> None:
        if graphics_compo.rect.bottom < 0:
            entities_manager.remove_entity_by_type_id_and_entity_id(shot_type_id, graphics_compo.entity_id)

    ecs.move_system(shots_list, shots_off_bounds_handler)


def move_bombs_system(bombs_list: List[List[ecs.Component]], bottom_edge: int, entities_manager: ecs.EntitiesManager,
                      bomb_type_id: int, explosions_factory: Callable[[int, int], int]) -> None:
    def bombs_off_bounds_handler(graphics_compo: ecs.GraphicsComponent, velocity_compo: ecs.VelocityComponent) -> None:
        if bottom_edge < graphics_compo.rect.bottom:
            explosions_factory(graphics_compo.rect.center[0], graphics_compo.rect.center[1])
            entities_manager.remove_entity_by_type_id_and_entity_id(bomb_type_id, graphics_compo.entity_id)

    ecs.move_system(bombs_list, bombs_off_bounds_handler)


def get_afv_collision_handler(alien_type_id: int, afv_rect: pygame.Rect, lives_id: int, curr_life: List[int],
                              life_penalty: int, explosion_factory: Callable[[int, int], int], screen: pygame.Surface,
                              background: pygame.Surface, dirty_rects: List[pygame.Rect]) \
        -> Callable[[Iterable[List[ecs.Component]], int, ecs.EntitiesManager], None]:
    def afv_collision_handler(collided_entities: List[List[ecs.Component]], collided_entity_idx: int,
                              entities_manager: ecs.EntitiesManager) -> None:
        curr_life[0] -= life_penalty
        ecs.rewrite_text_system(entities_manager.get_entity(lives_id), "Lives: {}".format(curr_life[0]), screen,
                                background, dirty_rects)
        explosion_factory(afv_rect.center[0], afv_rect.center[1])
        collided_entity_id = collided_entities[collided_entity_idx][0].entity_id
        if entities_manager.get_entity_type_id(collided_entity_id) == alien_type_id:
            alien_rect = ecs.get_component_of_entity(collided_entities[collided_entity_idx], ecs.GraphicsComponent).rect
            explosion_factory(alien_rect.center[0], alien_rect.center[1])
    return afv_collision_handler


def get_shot_at_aliens_handler(explosions_factory: Callable[[int, int], int], curr_score: List[int],
                               alien_hit_reward: int, score_id: int, screen: pygame.Surface, background: pygame.Surface,
                               dirty_rects: List[pygame.Rect]) \
        -> Callable[[List[ecs.Component], List[List[ecs.Component]], List[int], ecs.EntitiesManager], None]:
    def handle_shot_at_aliens(shot: List[ecs.Component], aliens: List[List[ecs.Component]],
                              collision_indices: List[int], entities_manager: ecs.EntitiesManager) -> None:
        killed_alien = aliens[collision_indices[0]]
        killed_alien_rect = ecs.get_component_of_entity(killed_alien, ecs.GraphicsComponent).rect
        explosions_factory(killed_alien_rect.center[0], killed_alien_rect.center[1])
        curr_score[0] += alien_hit_reward
        ecs.rewrite_text_system(entities_manager.get_entity(score_id), "Score: {}".format(curr_score[0]), screen,
                                background, dirty_rects)
        entities_manager.remove_entity(killed_alien)
        entities_manager.remove_entity(shot)

    return handle_shot_at_aliens
