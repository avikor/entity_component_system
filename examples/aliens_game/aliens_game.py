from sys import stderr
from typing import List, Dict, Tuple, Callable
from enum import IntEnum, unique
from random import random
from threading import Thread
import pygame
import ecs
from examples.aliens_game.aliens_game_systems import move_aliens_system, move_shots_system, move_bombs_system, \
    get_afv_collision_handler, get_shot_at_aliens_handler


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
    name_to_id_map = dict()

    background = pygame.Surface(screen_rect.size)
    for i in range(0, screen_rect.width, images[ImgsIndices.background_tile].get_width()):
        background.blit(images[ImgsIndices.background_tile], (i, 0))

    add_types_and_instantiate_entities(images, entities_manger, name_to_id_map)

    game_loop(screen, background, images, sounds, entities_manger, name_to_id_map)

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


def add_types_and_instantiate_entities(images: List[pygame.Surface], entities_manager: ecs.EntitiesManager,
                                       name_to_id_map: Dict[str, int]) -> None:
    instantiate_alien(images, entities_manager, name_to_id_map)
    add_bomb_type(entities_manager, name_to_id_map)
    instantiate_afv(images, entities_manager, name_to_id_map)
    add_shot_type(entities_manager, name_to_id_map)
    add_explosion_type(entities_manager, name_to_id_map)
    instantiate_score_and_lives(entities_manager, name_to_id_map)


def instantiate_alien(images: List[pygame.Surface], entities_manager: ecs.EntitiesManager,
                      name_to_id_map: Dict[str, int]) -> None:
    alien_type_id = entities_manager.add_entity_type([ecs.GraphicsComponent, ecs.AnimationCycleComponent,
                                                      ecs.VelocityComponent])
    name_to_id_map["alien_type_id"] = alien_type_id
    alien_graphics_compo = ecs.GraphicsComponent(images[ImgsIndices.alien1], ALIEN_INITIAL_POSITION[0],
                                                 ALIEN_INITIAL_POSITION[1])
    alien_ani_cycle_compo = ecs.AnimationCycleComponent((images[ImgsIndices.alien1], images[ImgsIndices.alien2],
                                                         images[ImgsIndices.alien3]), ALIEN_ANIMATION_INTERVAL_LENGTH)
    alien_velocity_compo = ecs.VelocityComponent(ALIEN_VELOCITY[0], ALIEN_VELOCITY[1])
    name_to_id_map["alien_id"] = entities_manager.instantiate_entity(alien_type_id, alien_graphics_compo,
                                                                     alien_ani_cycle_compo, alien_velocity_compo)


def add_bomb_type(entities_manager: ecs.EntitiesManager, name_to_id_map: Dict[str, int]) -> None:
    name_to_id_map["bomb_type_id"] = entities_manager.add_entity_type([ecs.GraphicsComponent, ecs.VelocityComponent])


def instantiate_afv(images: List[pygame.Surface], entities_manager: ecs.EntitiesManager,
                    name_to_id_map: Dict[str, int]) -> None:
    name_to_id_map["afv_type_id"] = entities_manager.add_entity_type([ecs.GraphicsComponent,
                                                                      ecs.HorizontalOrientationComponent,
                                                                      ecs.VelocityComponent])
    afv_graphics_compo = ecs.GraphicsComponent(images[ImgsIndices.afv], AFV_INITIAL_POSITION[0], AFV_INITIAL_POSITION[1])
    afv_hori_ori_compo = ecs.HorizontalOrientationComponent(images[ImgsIndices.afv],
                                                            pygame.transform.flip(images[ImgsIndices.afv], True, False))
    afv_velocity_compo = ecs.VelocityComponent(AFV_VELOCITY[0], AFV_VELOCITY[1])
    name_to_id_map["afv_id"] = entities_manager.instantiate_entity(name_to_id_map["afv_type_id"], afv_graphics_compo,
                                                                   afv_hori_ori_compo, afv_velocity_compo)


def add_shot_type(entities_manager: ecs.EntitiesManager, name_to_id_map: Dict[str, int]) -> None:
    name_to_id_map["shot_type_id"] = entities_manager.add_entity_type([ecs.GraphicsComponent, ecs.VelocityComponent,
                                                                       ecs.AudioComponent])


def add_explosion_type(entities_manager: ecs.EntitiesManager, name_to_id_map: Dict[str, int]) -> None:
    name_to_id_map["explosion_type_id"] = entities_manager.add_entity_type([ecs.GraphicsComponent,
                                                                            ecs.LifeTimeComponent, ecs.AudioComponent])


def instantiate_score_and_lives(entities_manager: ecs.EntitiesManager, name_to_id_map: Dict[str, int]) -> None:
    text_type_id = entities_manager.add_entity_type([ecs.GraphicsComponent, ecs.TextComponent])
    name_to_id_map["text_type_id"] = text_type_id

    lives_text_component = ecs.TextComponent("Lives: {}".format(INITIAL_PLAYER_LIFE), LIVES_TEXT_SIZE, LIVES_TEXT_COLOR)
    lives_surface = lives_text_component.font.render(lives_text_component.text, False, lives_text_component.color)
    lives_graphics_component = ecs.GraphicsComponent(lives_surface, LIVES_POSITION[0], LIVES_POSITION[1])
    lives_id = entities_manager.instantiate_entity(text_type_id, lives_graphics_component, lives_text_component)
    name_to_id_map["lives_id"] = lives_id

    score_text_component = ecs.TextComponent("Score: {}".format(INITIAL_PLAYER_SCORE), SCORE_TEXT_SIZE,
                                             SCORE_TEXT_COLOR)
    score_surface = score_text_component.font.render(score_text_component.text, False, score_text_component.color)
    score_graphics_component = ecs.GraphicsComponent(score_surface, SCORE_POSITION[0], SCORE_POSITION[1])
    score_id = entities_manager.instantiate_entity(text_type_id, score_graphics_component, score_text_component)
    name_to_id_map["score_id"] = score_id


def get_alien_factory(entities_manager: ecs.EntitiesManager, alien_type_id: int, alien_surface: pygame.Surface,
                      cyc_surfaces: Tuple[pygame.Surface, ...]) -> Callable[[int, int], int]:
    def alien_factory(initial_x: int, initial_y: int) -> int:
        graphics_compo = ecs.GraphicsComponent(alien_surface, initial_x, initial_y)
        ani_cycle_compo = ecs.AnimationCycleComponent(cyc_surfaces, ALIEN_ANIMATION_INTERVAL_LENGTH)
        velocity_compo = ecs.VelocityComponent(ALIEN_VELOCITY[0], ALIEN_VELOCITY[1])
        return entities_manager.instantiate_entity(alien_type_id, graphics_compo, ani_cycle_compo, velocity_compo)
    return alien_factory


def get_bomb_factory(entities_manager: ecs.EntitiesManager, bomb_type_id: int, bomb_surface: pygame.Surface) \
        -> Callable[[int, int], int]:
    def bomb_factory(initial_x: int, initial_y: int) -> int:
        graphics_compo = ecs.GraphicsComponent(bomb_surface, initial_x, initial_y)
        velocity_compo = ecs.VelocityComponent(BOMB_VELOCITY[0], BOMB_VELOCITY[1])
        return entities_manager.instantiate_entity(bomb_type_id, graphics_compo, velocity_compo)
    return bomb_factory


def get_shot_factory(entities_manager: ecs.EntitiesManager, shot_type_id: int, shot_surface: pygame.Surface,
                     shot_sound: pygame.mixer.Sound) -> Callable[[int, int], int]:
    def shot_factory(initial_x: int, initial_y: int) -> int:
        graphics_compo = ecs.GraphicsComponent(shot_surface, initial_x, initial_y)
        velocity_compo = ecs.VelocityComponent(SHOT_VELOCITY[0], SHOT_VELOCITY[1])
        audio_compo = ecs.AudioComponent(shot_sound)
        audio_compo.sound.play()
        return entities_manager.instantiate_entity(shot_type_id, graphics_compo, velocity_compo, audio_compo)
    return shot_factory


def get_explosion_factory(entities_manager: ecs.EntitiesManager, explosion_type_id: int,
                          explosion_surface: pygame.Surface,explosion_sound: pygame.mixer.Sound) \
        -> Callable[[int, int], int]:
    def explosion_factory(initial_x: int, initial_y: int) -> int:
        graphics_compo = ecs.GraphicsComponent(explosion_surface, initial_x, initial_y)
        lifetime_compo = ecs.LifeTimeComponent(EXPLOSION_LIFE_TIME)
        audio_compo = ecs.AudioComponent(explosion_sound)
        audio_compo.sound.play()
        return entities_manager.instantiate_entity(explosion_type_id, graphics_compo, lifetime_compo, audio_compo)
    return explosion_factory


def game_loop(screen: pygame.Surface, background: pygame.Surface, images: List[pygame.Surface],
              sounds: List[pygame.mixer.Sound], entities_manager: ecs.EntitiesManager,
              name_to_id_map: Dict[str, int]) -> None:
    alien_factory = get_alien_factory(entities_manager, name_to_id_map["alien_type_id"], images[ImgsIndices.alien1],
                                      (images[ImgsIndices.alien1], images[ImgsIndices.alien2],
                                       images[ImgsIndices.alien3]))
    bomb_factory = get_bomb_factory(entities_manager, name_to_id_map["bomb_type_id"], images[ImgsIndices.bomb])
    shot_factory = get_shot_factory(entities_manager, name_to_id_map["shot_type_id"], images[ImgsIndices.shot],
                                    sounds[SoundIndices.shot])
    explosion_factory = get_explosion_factory(entities_manager, name_to_id_map["explosion_type_id"],
                                              images[ImgsIndices.explosion], sounds[SoundIndices.explosion])

    right_edge = background.get_width()
    bomb_bottom_edge = background.get_height() - images[ImgsIndices.explosion].get_height() + BOMB_EDGE_OFFSET
    afv = entities_manager.get_entity(name_to_id_map["afv_id"])
    afv_rect = ecs.get_component_of_entity(afv, ecs.GraphicsComponent).rect

    is_player_reloading = False
    curr_life = [INITIAL_PLAYER_LIFE]
    curr_score = [INITIAL_PLAYER_SCORE]

    screen.blit(background, (0, 0))
    pygame.display.flip()
    sounds[SoundIndices.background_music].play(REPEAT_INDEFINITELY)
    clock = pygame.time.Clock()
    dirty_rects = list()

    while curr_life[0] > 0:
        pygame.event.pump()
        keys_state = pygame.key.get_pressed()
        if keys_state[pygame.K_ESCAPE] or pygame.event.peek(pygame.QUIT):
            break

        dirty_rects.extend(ecs.erase_system(screen, background,
                                            entities_manager.get_all_instances_of_component_class(ecs.
                                                                                                  GraphicsComponent)))

        explosions_list = list(entities_manager.get_all_entities_of_type(name_to_id_map["explosion_type_id"]))
        explosions_lifetime_handler = Thread(target=ecs.decrease_lifetime_system,
                                             args=(explosions_list, entities_manager,
                                                   name_to_id_map["explosion_type_id"]))
        explosions_lifetime_handler.start()

        if random() < ALIEN_INSTANTIATION_PROBABILITY:
            alien_factory(ALIEN_INITIAL_POSITION[0], ALIEN_INITIAL_POSITION[1])
        aliens_list = list(entities_manager.get_all_entities_of_type(name_to_id_map["alien_type_id"]))

        if aliens_list and random() < BOMB_INSTANTIATION_PROBABILITY:
            last_alien_rect = ecs.get_component_of_entity(aliens_list[-1], ecs.GraphicsComponent).rect
            if last_alien_rect.left > 0 and last_alien_rect.right < right_edge:
                bomb_initial_x, bomb_initial_y = last_alien_rect.move(BOMB_OFFSET[0], BOMB_OFFSET[1]).midbottom
                bomb_factory(bomb_initial_x, bomb_initial_y)
        bombs_list = list(entities_manager.get_all_entities_of_type(name_to_id_map["bomb_type_id"]))

        shots_list = list(entities_manager.get_all_entities_of_type(name_to_id_map["shot_type_id"]))
        if keys_state[pygame.K_SPACE] and not is_player_reloading and len(shots_list) < MAX_SHOTS_ON_SCREEN:
            shot_id = shot_factory(afv_rect.centerx, afv_rect.top - SHOT_OFFSET)
            shots_list.append(entities_manager.get_entity(shot_id))
        is_player_reloading = keys_state[pygame.K_SPACE]

        shots_mover = Thread(target=move_shots_system, args=(shots_list, entities_manager,
                                                             name_to_id_map["shot_type_id"]))
        shots_mover.start()

        aliens_mover = Thread(target=move_aliens_system, args=(aliens_list, right_edge))
        aliens_mover.start()

        aliens_colors_changer = Thread(target=ecs.rotate_animation_cycle_system, args=(aliens_list,))
        aliens_colors_changer.start()

        bombs_mover = Thread(target=move_bombs_system, args=(bombs_list, bomb_bottom_edge, entities_manager,
                                                             name_to_id_map["bomb_type_id"], explosion_factory))
        bombs_mover.start()

        x_direction = keys_state[pygame.K_RIGHT] - keys_state[pygame.K_LEFT]
        if x_direction != NO_MOVEMENT:
            ecs.move_screen_bounded_horizontally_oriented_entity_system(afv, x_direction, right_edge)

        shots_mover.join()
        aliens_mover.join()
        aliens_colors_changer.join()
        bombs_mover.join()

        aliens_collisions_handler = Thread(target=ecs.lists_collision_detection_with_handling_system,
                                           args=(shots_list, aliens_list, entities_manager,
                                                 get_shot_at_aliens_handler(explosion_factory, curr_score,
                                                                            ALIEN_HIT_REWARD,
                                                                            name_to_id_map["score_id"], screen,
                                                                            background, dirty_rects)))
        aliens_collisions_handler.start()

        afv_collision_handler = Thread(target=ecs.collision_detection_with_handling_system,
                                       args=(afv, bombs_list + aliens_list, entities_manager,
                                             get_afv_collision_handler(name_to_id_map["alien_type_id"], afv_rect,
                                                                       name_to_id_map["lives_id"], curr_life,
                                                                       LIFE_PENALTY, explosion_factory, screen,
                                                                       background, dirty_rects)))

        afv_collision_handler.start()

        aliens_collisions_handler.join()
        afv_collision_handler.join()
        explosions_lifetime_handler.join()

        dirty_rects.extend(ecs.draw_system(screen, entities_manager.get_all_instances_of_component_class(
            ecs.GraphicsComponent)))

        pygame.display.update(dirty_rects)
        dirty_rects.clear()
        clock.tick(FRAMES_PER_SECOND)

    pygame.mixer.fadeout(FADEOUT_TIME)
    pygame.time.wait(FADEOUT_TIME)


if __name__ == '__main__':
    run_aliens_game("aliens_game_resources/")
