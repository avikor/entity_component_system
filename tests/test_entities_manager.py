import unittest
import pygame
from ecs.component import GraphicsComponent, VelocityComponent, AnimationCycleComponent, \
    LifeTimeComponent, HorizontalOrientationComponent
from ecs.entities_manager import EntitiesManager, get_component_of_entity


class TestEntitiesManager(unittest.TestCase):
    def setUp(self):
        self.entities_manager = EntitiesManager()
        self.name_to_id_map = dict()
        self.name_to_id_map["alien_type_id"] = self.entities_manager.add_entity_type([GraphicsComponent,
                                                                                      AnimationCycleComponent,
                                                                                      VelocityComponent])
        self.name_to_id_map["explosion_type_id"] = self.entities_manager.\
            add_entity_type([GraphicsComponent, LifeTimeComponent, HorizontalOrientationComponent])
        alien1_graphics_compo = GraphicsComponent(pygame.Surface((13, 13)), 0, 0)
        alien_ani_cycle_compo = AnimationCycleComponent((pygame.Surface((13, 13)),
                                                         pygame.Surface((13, 13)),
                                                         pygame.Surface((13, 13))), 12)
        alien_velo_compo = VelocityComponent(1, 1)
        self.name_to_id_map["alien1_id"] = self.entities_manager.instantiate_entity(
            self.name_to_id_map["alien_type_id"], alien1_graphics_compo, alien_ani_cycle_compo, alien_velo_compo)

        alien2_graphics_compo = GraphicsComponent(pygame.Surface((13, 13)), 0, 0)
        self.name_to_id_map["alien2_id"] = self.entities_manager.instantiate_entity(
            self.name_to_id_map["alien_type_id"], alien2_graphics_compo, alien_ani_cycle_compo, VelocityComponent(0, 0))

        explosion_graphics_compo = GraphicsComponent(pygame.Surface((13, 13)), 0, 0)
        explosion_lifetime_compo = LifeTimeComponent(12)
        hori_ori_compo = HorizontalOrientationComponent(pygame.Surface((13, 13)), pygame.Surface((13, 13)))
        self.name_to_id_map["explosion1_id"] = self.entities_manager.instantiate_entity(
            self.name_to_id_map["explosion_type_id"], explosion_graphics_compo, explosion_lifetime_compo,
            hori_ori_compo)

    def test_get_all_entities_ids(self):
        self.assertEqual(self.entities_manager.get_all_entities_ids(), {self.name_to_id_map["alien1_id"],
                                                                        self.name_to_id_map["alien2_id"],
                                                                        self.name_to_id_map["explosion1_id"]})

    def test_get_all_entities(self):
        all_ents = [self.entities_manager.get_entity(self.name_to_id_map["alien1_id"]),
                    self.entities_manager.get_entity(self.name_to_id_map["alien2_id"]),
                    self.entities_manager.get_entity(self.name_to_id_map["explosion1_id"])]
        self.assertEqual(list(self.entities_manager.get_all_entities()), all_ents)

    def test_get_all_entities_type_ids(self):
        self.assertEqual(self.entities_manager.get_all_entities_type_ids(), {self.name_to_id_map["alien_type_id"],
                                                                             self.name_to_id_map["explosion_type_id"]})

    def test_get_all_component_classes_names(self):
        all_names = {"GraphicsComponent", "AnimationCycleComponent", "VelocityComponent", "LifeTimeComponent",
                     "HorizontalOrientationComponent"}
        self.assertEqual(self.entities_manager.get_all_component_classes_names(), all_names)

    def test_get_all_entities_of_type(self):
        aliens = [self.entities_manager.get_entity(self.name_to_id_map["alien1_id"]),
                  self.entities_manager.get_entity(self.name_to_id_map["alien2_id"])]
        self.assertEqual(list(self.entities_manager.get_all_entities_of_type(self.name_to_id_map["alien_type_id"])),
                         aliens)
        explosions = [self.entities_manager.get_entity(self.name_to_id_map["explosion1_id"])]
        self.assertEqual(list(self.entities_manager.get_all_entities_of_type(self.name_to_id_map["explosion_type_id"])),
                         explosions)

    def test_get_all_entities_with_component_class(self):
        explosions = [self.entities_manager.get_entity(self.name_to_id_map["explosion1_id"])]
        self.assertEqual(list(self.entities_manager.get_all_entities_with_component_class(LifeTimeComponent)),
                         explosions)
        aliens = [self.entities_manager.get_entity(self.name_to_id_map["alien1_id"]),
                  self.entities_manager.get_entity(self.name_to_id_map["alien2_id"])]
        self.assertEqual(list(self.entities_manager.get_all_entities_with_component_class(VelocityComponent)),
                         aliens)

    def test_get_all_instances_of_component_class(self):
        explosion_lifetime_compo = [get_component_of_entity(self.entities_manager.get_entity(
            self.name_to_id_map["explosion1_id"]), LifeTimeComponent)]
        self.assertEqual(list(self.entities_manager.get_all_instances_of_component_class(LifeTimeComponent)),
                         explosion_lifetime_compo)
        alien1_any_cycle = get_component_of_entity(self.entities_manager.get_entity(self.name_to_id_map["alien1_id"]),
                                                   AnimationCycleComponent)
        alien2_any_cycle = get_component_of_entity(self.entities_manager.get_entity(self.name_to_id_map["alien2_id"]),
                                                   AnimationCycleComponent)
        self.assertEqual(list(self.entities_manager.get_all_instances_of_component_class(AnimationCycleComponent)),
                         [alien1_any_cycle, alien2_any_cycle])

    def test_get_entity_type_component_classes_names(self):
        self.assertEqual(set(self.entities_manager.get_entity_type_component_classes_names(
            self.name_to_id_map["alien_type_id"])), {"GraphicsComponent", "AnimationCycleComponent",
                                                     "VelocityComponent"})

    def test_get_entity_id(self):
        alien1 = self.entities_manager.get_entity(self.name_to_id_map["alien1_id"])
        self.assertEqual(self.entities_manager.get_entity_id(alien1), self.name_to_id_map["alien1_id"])

    def test_get_entity_type_id(self):
        self.assertEqual(self.name_to_id_map["alien_type_id"],
                         self.entities_manager.get_entity_type_id(self.name_to_id_map["alien1_id"]))

    def test_remove_entity_by_type_id_and_entity_id(self):
        self.entities_manager.remove_entity_by_type_id_and_entity_id(self.name_to_id_map["explosion_type_id"],
                                                                     self.name_to_id_map["explosion1_id"])
        self.assertEqual(self.entities_manager.get_all_entities_ids(), {self.name_to_id_map["alien1_id"],
                                                                        self.name_to_id_map["alien2_id"]})

    def test_remove_entity(self):
        explosion = self.entities_manager.get_entity(self.name_to_id_map["explosion1_id"])
        self.entities_manager.remove_entity(explosion)
        self.assertEqual(self.entities_manager.get_all_entities_ids(), {self.name_to_id_map["alien1_id"],
                                                                        self.name_to_id_map["alien2_id"]})

    def test_remove_entity_type_and_its_instances(self):
        self.entities_manager.remove_entity_type_and_its_instances(self.name_to_id_map["alien_type_id"])
        self.assertEqual(self.entities_manager.get_all_entities_ids(), {self.name_to_id_map["explosion1_id"]})
        self.assertEqual(self.entities_manager.get_all_component_classes_names(), {"GraphicsComponent",
                                                                                   "LifeTimeComponent",
                                                                                   "HorizontalOrientationComponent"})


if __name__ == '__main__':
    unittest.main()
