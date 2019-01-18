from typing import Any, Iterator, Dict
from collections import OrderedDict


Entity = Dict[str, Any]


class EntitiesManager:
    def __init__(self):
        self.__compo_class_name_to_entities = OrderedDict()      # 1. Dict[str, List[Entity]]
        self.__group_to_entities = OrderedDict()                 # 2. Dict[Any, List[Entity]]

    def register_entity(self, entity: Entity) -> None:
        for compo_class_name in entity:
            if compo_class_name not in self.__compo_class_name_to_entities:
                self.__compo_class_name_to_entities[compo_class_name] = list()
            self.__compo_class_name_to_entities[compo_class_name].append(entity)

    def unregister_entity(self, entity: Entity):
        for compo_class_name in entity:
            self.__compo_class_name_to_entities[compo_class_name].remove(entity)

    def add_group(self, group_name: Any) -> None:
        if group_name in self.__group_to_entities:
            raise OccupiedNameError()
        self.__group_to_entities[group_name] = list()

    def enlist_entity_to_group(self, group_name: Any, entity: Entity) -> None:
        self.__group_to_entities[group_name].append(entity)

    def discharge_entity_from_group(self, group_name: Any, entity: Entity) -> None:
        self.__group_to_entities[group_name].remove(entity)

    def discharge_entity_from_all_groups(self, entity: Entity) -> None:
        for group_name in self.__group_to_entities:
            if entity in self.__group_to_entities[group_name]:
                self.__group_to_entities[group_name].remove(entity)

    def delete_group(self, group_name: Any) -> None:
        del self.__group_to_entities[group_name]

    def delete_group_and_its_entities(self, group_name: Any) -> None:
        for entity in self.__group_to_entities[group_name]:
            for compo_class_name in entity:
                self.__compo_class_name_to_entities[compo_class_name].remove(entity)
        del self.__group_to_entities[group_name]

    def unregister_and_discharge_entity_from_all_groups(self, entity: Entity) -> None:
        self.discharge_entity_from_all_groups(entity)
        self.unregister_entity(entity)

    def register_and_enlist_entity(self, entity: Entity, *groups_names) -> None:
        self.register_entity(entity)
        for group_name in groups_names:
            if group_name not in self.__group_to_entities:
                self.__group_to_entities[group_name] = list()
            self.__group_to_entities[group_name].append(entity)

    def get_entity_groups(self, entity: Entity) -> set:
        groups = set()
        for group_name in self.__group_to_entities:
            if entity in self.__group_to_entities[group_name]:
                groups.add(group_name)
        return groups

    def get_all_entities_of_group(self, group_name: Any) -> Iterator[Entity]:
        def group_entities_generator() -> Iterator[Entity]:
            for entity in self.__group_to_entities[group_name]:
                yield entity
        return group_entities_generator()

    def get_all_entities_with_component_class(self, compo_class_name: str) -> Iterator[Entity]:
        def compo_entities_generator() -> Iterator[Entity]:
            for entity in self.__compo_class_name_to_entities[compo_class_name]:
                yield entity
        return compo_entities_generator()

    def get_all_instances_of_component_class(self, compo_class_name: str) -> Iterator[Any]:
        def compo_instances_generator() -> Iterator[Any]:
            for entity in self.__compo_class_name_to_entities[compo_class_name]:
                yield entity[compo_class_name]
        return compo_instances_generator()


class OccupiedNameError(LookupError):
    def __init__(self):
        super(OccupiedNameError, self).__init__("Name for group already in use.")
