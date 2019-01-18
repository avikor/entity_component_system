from sys import stderr
from typing import List, Tuple, Callable, Iterable
from enum import IntEnum, unique
from random import random
from threading import Thread
import pygame
import ecs


RESOLUTION = 640, 480
SCREEN_CAPTION = "The Illustrious Aliens Game"
IMAGES_FORMAT = ".gif"
SOUND_FORMAT = ".wav"
FRAMES_PER_SECOND = 40
ALIEN_INITIAL_POSITION = 0, 0
AFV_INITIAL_POSITION = 320, 420
ALIEN_VELOCITY = 13, 0
BOMB_VELOCITY = 0, 9
AFV_VELOCITY = 10, 0
SHOT_VELOCITY = 0, -11
NO_MOVEMENT = 0
NO_COLLISIONS = -1
REPEAT_INDEFINITELY = -1
SCORE_POSITION = 10, 450
SCORE_TEXT_SIZE = 20
SCORE_TEXT_COLOR = "white"
LIVES_POSITION = 10, 465
LIVES_TEXT_SIZE = 20
LIVES_TEXT_COLOR = "white"
ALIEN_HIT_REWARD = 10
LIFE_PENALTY = 1
INITIAL_PLAYER_LIFE = 1
INITIAL_PLAYER_SCORE = 0
ALIEN_INSTANTIATION_PROBABILITY = 0.02
BOMB_INSTANTIATION_PROBABILITY = 0.02
MAX_SHOTS_ON_SCREEN = 2
SHOT_OFFSET = 10
BOMB_OFFSET = 0, 5
BOMB_EDGE_OFFSET = 50
EXPLOSION_LIFE_TIME = 6
ALIEN_ANIMATION_INTERVAL_LENGTH = 12
FADEOUT_TIME = 1000


def run_aliens_game(path_to_resources: str) -> None:
    pygame.init()
    screen = pygame.display.set_mode(RESOLUTION)
    screen_rect = screen.get_rect()
    pygame.display.set_caption(SCREEN_CAPTION)
    images = load_images(path_to_resources)
    sounds = load_sounds(path_to_resources)
    entities_manger = ecs.EntitiesManager()

    background = pygame.Surface(screen_rect.size)
    for i in range(0, screen_rect.width, images[ImgsIndices.background_tile].get_width()):
        background.blit(images[ImgsIndices.background_tile], (i, 0))

    afv, lives, score = dict(), dict(), dict()
    add_groups_and_create_entities(images, entities_manger, afv, lives, score)

    game_loop(screen, background, images, sounds, entities_manger, afv, lives, score)

    pygame.quit()


@unique
class ImgsIndices(IntEnum):
    # enum is iterated by definition order, so keep member definition ordered by ascending int values
    background_tile = 0
    alien1 = 1
    alien2 = 2
    alien3 = 3
    afv = 4
    bomb = 5
    shot = 6
    explosion = 7


def load_images(path: str) -> List[pygame.Surface]:
    surfaces = list()
    for image_idx in ImgsIndices:
        try:
            surfaces.append(pygame.image.load(path + image_idx.name + IMAGES_FORMAT))
        except pygame.error:
            print(pygame.get_error(), file=stderr)
            exit(-1)
    return surfaces


@unique
class SoundIndices(IntEnum):
    # enum is iterated by definition order, so keep member definition ordered by ascending int values
    background_music = 0
    shot = 1
    explosion = 2


def load_sounds(path: str) -> List[pygame.mixer.Sound]:
    sounds = list()
    for sound_idx in SoundIndices:
        try:
            sounds.append(pygame.mixer.Sound(path + sound_idx.name + SOUND_FORMAT))
        except pygame.error:
            print(pygame.get_error(), file=stderr)
            exit(-1)
    return sounds


def add_groups_and_create_entities(images: List[pygame.Surface], entities_manager: ecs.EntitiesManager, afv: ecs.Entity,
                                   lives: ecs.Entity, score: ecs.Entity) -> None:
    register_and_enlist_alien(images, entities_manager)
    add_bombs_group(entities_manager)
    register_afv(images[ImgsIndices.afv], entities_manager, afv)
    add_shots_group(entities_manager)
    add_explosions_group(entities_manager)
    register_lives(entities_manager, lives)
    register_score(entities_manager, score)


def register_and_enlist_alien(images: List[pygame.Surface],
                              entities_manager: ecs.EntitiesManager) -> None:
    alien = dict()
    alien["GraphicComponent"] = ecs.GraphicComponent(images[ImgsIndices.alien1], ALIEN_INITIAL_POSITION[0],
                                                     ALIEN_INITIAL_POSITION[1])
    alien["AnimationCycleComponent"] = ecs.AnimationCycleComponent((images[ImgsIndices.alien1],
                                                                    images[ImgsIndices.alien2],
                                                                    images[ImgsIndices.alien3]),
                                                                   ALIEN_ANIMATION_INTERVAL_LENGTH)
    alien["VelocityComponent"] = ecs.VelocityComponent(ALIEN_VELOCITY[0], ALIEN_VELOCITY[1])
    entities_manager.register_and_enlist_entity(alien, "aliens")


def add_bombs_group(entities_manager: ecs.EntitiesManager) -> None:
    entities_manager.add_group("bombs")


def register_afv(afv_surface: pygame.Surface, entities_manager: ecs.EntitiesManager, afv: ecs.Entity) -> None:
    afv["GraphicComponent"] = ecs.GraphicComponent(afv_surface, AFV_INITIAL_POSITION[0], AFV_INITIAL_POSITION[1])
    afv["HorizontalOrientationComponent"] = ecs.HorizontalOrientationComponent(afv_surface,
                                                                               pygame.transform.flip(afv_surface, True,
                                                                                                     False))
    afv["VelocityComponent"] = ecs.VelocityComponent(AFV_VELOCITY[0], AFV_VELOCITY[1])
    entities_manager.register_entity(afv)


def add_shots_group(entities_manager: ecs.EntitiesManager) -> None:
    entities_manager.add_group("shots")


def add_explosions_group(entities_manager: ecs.EntitiesManager) -> None:
    entities_manager.add_group("explosions")


def register_lives(entities_manager: ecs.EntitiesManager, lives: ecs.Entity) -> None:
    lives["TextComponent"] = ecs.TextComponent("Lives: {}".format(INITIAL_PLAYER_LIFE), LIVES_TEXT_SIZE,
                                               LIVES_TEXT_COLOR)
    lives_surface = lives["TextComponent"].font.render(lives["TextComponent"].text, False, lives["TextComponent"].color)
    lives["GraphicComponent"] = ecs.GraphicComponent(lives_surface, LIVES_POSITION[0], LIVES_POSITION[1])
    entities_manager.register_entity(lives)


def register_score(entities_manager: ecs.EntitiesManager, score: ecs.Entity) -> None:
    score["TextComponent"] = ecs.TextComponent("Score: {}".format(INITIAL_PLAYER_SCORE), SCORE_TEXT_SIZE,
                                               SCORE_TEXT_COLOR)
    score_surface = score["TextComponent"].font.render(score["TextComponent"].text, False, score["TextComponent"].color)
    score["GraphicComponent"] = ecs.GraphicComponent(score_surface, SCORE_POSITION[0], SCORE_POSITION[1])
    entities_manager.register_entity(score)


def game_loop(screen: pygame.Surface, background: pygame.Surface, images: List[pygame.Surface],
              sounds: List[pygame.mixer.Sound], entities_manager: ecs.EntitiesManager, afv: ecs.Entity,
              lives: ecs.Entity, score: ecs.Entity) -> None:
    alien_factory = get_aliens_factory(images[ImgsIndices.alien1], (images[ImgsIndices.alien1],
                                                                    images[ImgsIndices.alien2],
                                                                    images[ImgsIndices.alien3]), entities_manager)
    bomb_factory = get_bomb_factory(images[ImgsIndices.bomb], entities_manager)
    shot_factory = get_shot_factory(images[ImgsIndices.shot], sounds[SoundIndices.shot], entities_manager)
    explosion_factory = get_explosion_factory(images[ImgsIndices.explosion], sounds[SoundIndices.explosion],
                                              entities_manager)

    right_edge = background.get_width()
    bomb_bottom_edge = background.get_height() - images[ImgsIndices.explosion].get_height() + BOMB_EDGE_OFFSET
    afv_rect = afv["GraphicComponent"].rect

    afv_off_bounds_handler = get_afv_off_bounds_handler(right_edge)
    aliens_off_bounds_handler = get_aliens_off_bounds_handler(right_edge)
    shots_off_bounds_handler = get_shots_off_bounds_handler(entities_manager)
    bombs_off_bounds_handler = get_bombs_off_bounds_handler(entities_manager, bomb_bottom_edge, explosion_factory)

    is_player_reloading = False
    curr_life = [INITIAL_PLAYER_LIFE]
    curr_score = [INITIAL_PLAYER_SCORE]
    dirty_rects = list()

    handle_afv_collision = get_afv_collision_handler(afv_rect, lives, curr_life, LIFE_PENALTY, explosion_factory,
                                                     screen, background, dirty_rects)
    shot_at_aliens_handler = get_shot_at_aliens_handler(explosion_factory, curr_score, ALIEN_HIT_REWARD, score, screen,
                                                        background, dirty_rects)

    screen.blit(background, (0, 0))
    pygame.display.flip()
    sounds[SoundIndices.background_music].play(REPEAT_INDEFINITELY)
    clock = pygame.time.Clock()

    while curr_life[0] > 0:
        pygame.event.pump()
        keys_state = pygame.key.get_pressed()
        if keys_state[pygame.K_ESCAPE] or pygame.event.peek(pygame.QUIT):
            break

        ecs.erase_system(screen, background,
                         entities_manager.get_all_instances_of_component_class("GraphicComponent"), dirty_rects)

        explosions_list = list(entities_manager.get_all_entities_of_group("explosions"))
        explosions_lifetime_handler = Thread(target=ecs.decrease_lifetime_system,
                                             args=(explosions_list, entities_manager))
        explosions_lifetime_handler.start()

        if random() < ALIEN_INSTANTIATION_PROBABILITY:
            alien_factory(ALIEN_INITIAL_POSITION[0], ALIEN_INITIAL_POSITION[1])
        aliens_list = list(entities_manager.get_all_entities_of_group("aliens"))

        if aliens_list and random() < BOMB_INSTANTIATION_PROBABILITY:
            last_alien_rect = aliens_list[-1]["GraphicComponent"].rect
            if last_alien_rect.left > 0 and last_alien_rect.right < right_edge:
                bomb_initial_x, bomb_initial_y = last_alien_rect.move(BOMB_OFFSET[0], BOMB_OFFSET[1]).midbottom
                bomb_factory(bomb_initial_x, bomb_initial_y)
        bombs_list = list(entities_manager.get_all_entities_of_group("bombs"))

        shots_list = list(entities_manager.get_all_entities_of_group("shots"))
        if keys_state[pygame.K_SPACE] and not is_player_reloading and len(shots_list) < MAX_SHOTS_ON_SCREEN:
            newest_shot = shot_factory(afv_rect.centerx, afv_rect.top - SHOT_OFFSET)
            shots_list.append(newest_shot)
        is_player_reloading = keys_state[pygame.K_SPACE]

        shots_mover = Thread(target=ecs.move_system, args=(shots_list, shots_off_bounds_handler))
        shots_mover.start()

        aliens_mover = Thread(target=ecs.move_system, args=(aliens_list, aliens_off_bounds_handler))
        aliens_mover.start()

        aliens_colors_changer = Thread(target=ecs.rotate_animation_cycle_system, args=(aliens_list,))
        aliens_colors_changer.start()

        bombs_mover = Thread(target=ecs.move_system, args=(bombs_list, bombs_off_bounds_handler))
        bombs_mover.start()

        x_direction = keys_state[pygame.K_RIGHT] - keys_state[pygame.K_LEFT]
        if x_direction != NO_MOVEMENT:
            ecs.move_horizontally_oriented_entity_system(afv, x_direction, afv_off_bounds_handler)

        shots_mover.join()
        aliens_mover.join()
        aliens_colors_changer.join()
        bombs_mover.join()

        aliens_collisions_handler = Thread(target=ecs.lists_collision_detection_with_handling_system,
                                           args=(shots_list, aliens_list, entities_manager,
                                                 shot_at_aliens_handler))
        aliens_collisions_handler.start()

        afv_collision_handler = Thread(target=ecs.collision_detection_with_handling_system,
                                       args=(afv, bombs_list + aliens_list, entities_manager,
                                             handle_afv_collision))
        afv_collision_handler.start()

        aliens_collisions_handler.join()
        afv_collision_handler.join()
        explosions_lifetime_handler.join()

        ecs.draw_system(screen, entities_manager.get_all_instances_of_component_class("GraphicComponent"), dirty_rects)

        pygame.display.update(dirty_rects)
        dirty_rects.clear()
        clock.tick(FRAMES_PER_SECOND)

    pygame.mixer.fadeout(FADEOUT_TIME)
    pygame.time.wait(FADEOUT_TIME)


def get_aliens_factory(alien_surface: pygame.Surface, cyc_surfaces: Tuple[pygame.Surface, ...],
                       entities_manager: ecs.EntitiesManager) -> Callable[[int, int], ecs.Entity]:
    def alien_factory(initial_x: int, initial_y: int) -> ecs.Entity:
        alien = dict()
        alien["GraphicComponent"] = ecs.GraphicComponent(alien_surface, initial_x, initial_y)
        alien["AnimationCycleComponent"] = ecs.AnimationCycleComponent(cyc_surfaces, ALIEN_ANIMATION_INTERVAL_LENGTH)
        alien["VelocityComponent"] = ecs.VelocityComponent(ALIEN_VELOCITY[0], ALIEN_VELOCITY[1])
        entities_manager.register_and_enlist_entity(alien, "aliens")
        return alien
    return alien_factory


def get_bomb_factory(bomb_surface: pygame.Surface, entities_manager: ecs.EntitiesManager) \
        -> Callable[[int, int], ecs.Entity]:
    def bomb_factory(initial_x: int, initial_y: int) -> ecs.Entity:
        bomb = dict()
        bomb["GraphicComponent"] = ecs.GraphicComponent(bomb_surface, initial_x, initial_y)
        bomb["VelocityComponent"] = ecs.VelocityComponent(BOMB_VELOCITY[0], BOMB_VELOCITY[1])
        entities_manager.register_and_enlist_entity(bomb, "bombs")
        return bomb
    return bomb_factory


def get_shot_factory(shot_surface: pygame.Surface, shot_sound: pygame.mixer.Sound,
                     entities_manager: ecs.EntitiesManager) -> Callable[[int, int], ecs.Entity]:
    def shot_factory(initial_x: int, initial_y: int) -> ecs.Entity:
        shot = dict()
        shot["GraphicComponent"] = ecs.GraphicComponent(shot_surface, initial_x, initial_y)
        shot["VelocityComponent"] = ecs.VelocityComponent(SHOT_VELOCITY[0], SHOT_VELOCITY[1])
        shot["AudioComponent"] = ecs.AudioComponent(shot_sound)
        shot["AudioComponent"].sound.play()
        entities_manager.register_and_enlist_entity(shot, "shots")
        return shot
    return shot_factory


def get_explosion_factory(explosion_surface: pygame.Surface, explosion_sound: pygame.mixer.Sound,
                          entities_manager: ecs.EntitiesManager) -> Callable[[int, int], ecs.Entity]:
    def explosion_factory(initial_x: int, initial_y: int) -> ecs.Entity:
        explosion = dict()
        explosion["GraphicComponent"] = ecs.GraphicComponent(explosion_surface, initial_x, initial_y)
        explosion["LifeTimeComponent"] = ecs.LifeTimeComponent(EXPLOSION_LIFE_TIME)
        explosion["AudioComponent"] = ecs.AudioComponent(explosion_sound)
        explosion["AudioComponent"].sound.play()
        entities_manager.register_and_enlist_entity(explosion, "explosions")
        return explosion
    return explosion_factory


def get_afv_off_bounds_handler(right_edge: int) -> Callable[[ecs.Entity], None]:
    def afv_off_bounds_handler(afv: ecs.Entity) -> None:
        afv["GraphicComponent"].rect.left = max(afv["GraphicComponent"].rect.left, 0)
        afv["GraphicComponent"].rect.right = min(afv["GraphicComponent"].rect.right, right_edge)
    return afv_off_bounds_handler


def get_aliens_off_bounds_handler(right_edge: int) -> Callable[[ecs.Entity], None]:
    def aliens_off_bounds_handler(entity: ecs.Entity) -> None:
        graphic_compo = entity["GraphicComponent"]
        velocity_compo = entity["VelocityComponent"]
        if graphic_compo.rect.left > right_edge:
            graphic_compo.rect.left = right_edge
        elif graphic_compo.rect.right < 0:
            graphic_compo.rect.right = 0
        if graphic_compo.rect.left == right_edge or graphic_compo.rect.right == 0:
            velocity_compo.x_velocity *= -1
            graphic_compo.rect.top = graphic_compo.rect.bottom + 1
    return aliens_off_bounds_handler


def get_shots_off_bounds_handler(entities_manager: ecs.EntitiesManager) -> Callable[[ecs.Entity], None]:
    def shots_off_bounds_handler(entity: ecs.Entity) -> None:
        graphic_compo = entity["GraphicComponent"]
        if graphic_compo.rect.bottom < 0:
            entities_manager.unregister_and_discharge_entity_from_all_groups(entity)
    return shots_off_bounds_handler


def get_bombs_off_bounds_handler(entities_manager: ecs.EntitiesManager, bottom_edge: int,
                                 explosions_factory: Callable[[int, int], ecs.Entity]) -> Callable[[ecs.Entity], None]:
    def bombs_off_bounds_handler(entity: ecs.Entity) -> None:
        graphic_compo = entity["GraphicComponent"]
        if bottom_edge < graphic_compo.rect.bottom:
            explosions_factory(graphic_compo.rect.center[0], graphic_compo.rect.center[1])
            entities_manager.unregister_and_discharge_entity_from_all_groups(entity)
    return bombs_off_bounds_handler


def get_afv_collision_handler(afv_rect: pygame.Rect, lives: ecs.Entity, curr_life: List[int],
                              life_penalty: int, explosion_factory: Callable[[int, int], ecs.Entity],
                              screen: pygame.Surface, background: pygame.Surface, dirty_rects: List[pygame.Rect]) \
        -> Callable[[Iterable[ecs.Entity], int, ecs.EntitiesManager], None]:
    def afv_collision_handler(collided_entities: List[ecs.Entity], collided_entity_idx: int,
                              entities_manager: ecs.EntitiesManager) -> None:
        curr_life[0] -= life_penalty
        ecs.rewrite_text_system(screen, background, dirty_rects, lives, "Lives: {}".format(curr_life[0]))
        explosion_factory(afv_rect.center[0], afv_rect.center[1])
        collided_entity_groups = entities_manager.get_entity_groups(collided_entities[collided_entity_idx])
        if "aliens" in collided_entity_groups:
            alien_rect = collided_entities[collided_entity_idx]["GraphicComponent"].rect
            explosion_factory(alien_rect.center[0], alien_rect.center[1])
    return afv_collision_handler


def get_shot_at_aliens_handler(explosions_factory: Callable[[int, int], ecs.Entity], curr_score: List[int],
                               alien_hit_reward: int, score: ecs.Entity, screen: pygame.Surface,
                               background: pygame.Surface, dirty_rects: List[pygame.Rect]) \
        -> Callable[[ecs.Entity, List[ecs.Entity], List[int], ecs.EntitiesManager], None]:
    def shot_at_aliens_handler(shot: ecs.Entity, aliens: List[ecs.Entity],
                               collision_indices: List[int], entities_manager: ecs.EntitiesManager) -> None:
        killed_alien = aliens[collision_indices[0]]
        killed_alien_rect = killed_alien["GraphicComponent"].rect
        explosions_factory(killed_alien_rect.center[0], killed_alien_rect.center[1])
        curr_score[0] += alien_hit_reward
        ecs.rewrite_text_system(screen, background, dirty_rects, score, "Score: {}".format(curr_score[0]))
        entities_manager.unregister_and_discharge_entity_from_all_groups(killed_alien)
        entities_manager.unregister_and_discharge_entity_from_all_groups(shot)
    return shot_at_aliens_handler


if __name__ == '__main__':
    run_aliens_game("aliens_game_resources/")
