from random import getrandbits
from collections import OrderedDict
from typing import Iterator, Type, List, ValuesView, KeysView, Any
from operator import attrgetter
from ecs.component import Component


RANDOM_BITS_AMOUNT = 32


def _generate_unique_id() -> Iterator[int]:
    seed = getrandbits(RANDOM_BITS_AMOUNT)
    while True:
        yield seed
        seed += 1


_name_getter = attrgetter("__name__")


class EntitiesManager:
    def __init__(self) -> None:
        self.__id_to_entity = OrderedDict()                             # 1. Dict[int, List[Component]]
        self.__type_id_to_component_classes_names = OrderedDict()       # 2. Dict[int, List[str]
        self.__type_id_to_entities_ids = OrderedDict()                  # 3. Dict[int, List[int]]
        self.__component_class_name_to_entities_ids = OrderedDict()     # 4. Dict[str, List[int]]

    def get_all_entities_ids(self) -> KeysView:
        return self.__id_to_entity.keys()

    def get_all_entities(self) -> ValuesView:
        return self.__id_to_entity.values()

    def get_all_entities_type_ids(self) -> KeysView:
        return self.__type_id_to_entities_ids.keys()

    def get_all_component_classes_names(self) -> KeysView:
        return self.__component_class_name_to_entities_ids.keys()

    def get_all_entities_of_type(self, type_id: int) -> Iterator[list]:
        def entities_of_type_generator() -> Iterator[list]:
            for entity_id in self.__type_id_to_entities_ids[type_id]:
                yield self.__id_to_entity[entity_id]
        return entities_of_type_generator()

    def get_all_entities_with_component_class(self, component_class: Type[Component]) -> Iterator[list]:
        def entities_composed_of_component_generator() -> Iterator[list]:
            for entity_id in self.__component_class_name_to_entities_ids[component_class.__name__]:
                yield self.__id_to_entity[entity_id]
        return entities_composed_of_component_generator()

    def get_all_instances_of_component_class(self, component_class: Type[Component]) -> Iterator[Any]:
        def instances_of_component_class_generator() -> Iterator[Any]:
            for entity_id in self.__component_class_name_to_entities_ids[component_class.__name__]:
                for component_instance in self.__id_to_entity[entity_id]:
                    if isinstance(component_instance, component_class):
                        yield component_instance
        return instances_of_component_class_generator()

    def get_entity_type_component_classes_names(self, type_id: int) -> List[str]:
        return self.__type_id_to_component_classes_names[type_id]

    def get_entity(self, entity_id: int) -> List[Component]:
        return self.__id_to_entity[entity_id]

    def get_entity_id(self, given_entity: List[Component]) -> int:
        for entity_id, entity in self.__id_to_entity.items():
            if entity == given_entity:
                return entity_id
        raise ValueError()

    def get_entity_type_id(self, entity_id: int) -> int:
        for type_id, instances_ids in self.__type_id_to_entities_ids.items():
            if entity_id in instances_ids:
                return type_id
        raise ValueError()

    def add_entity_type(self, component_classes: List[Type[Component]]) -> int:
        type_id = next(_generate_unique_id())
        self.__type_id_to_component_classes_names[type_id] = list(map(_name_getter, component_classes))
        self.__type_id_to_entities_ids[type_id] = list()
        for compo_class in component_classes:
            if compo_class.__name__ not in self.__component_class_name_to_entities_ids:
                self.__component_class_name_to_entities_ids[compo_class.__name__] = list()
        return type_id

    def instantiate_entity(self, type_id: int, *components) -> int:
        for component, compo_class_name in zip(components, self.__type_id_to_component_classes_names[type_id]):
            if component.__class__.__name__ != compo_class_name:
                raise TypeError()

        entity_id = next(_generate_unique_id())
        self.__id_to_entity[entity_id] = list(components)
        self.__type_id_to_entities_ids[type_id].append(entity_id)
        for component in components:
            component.entity_id = entity_id
            self.__component_class_name_to_entities_ids[component.__class__.__name__].append(entity_id)
        return entity_id

    def remove_entity_by_type_id_and_entity_id(self, type_id: int, entity_id: int) -> None:
        for component in self.__id_to_entity[entity_id]:
            self.__component_class_name_to_entities_ids[component.__class__.__name__].remove(entity_id)
        self.__type_id_to_entities_ids[type_id].remove(entity_id)
        del self.__id_to_entity[entity_id]

    def remove_entity(self, entity: List[Component]) -> None:
        entity_id = self.get_entity_id(entity)
        type_id = self.get_entity_type_id(entity_id)
        self.remove_entity_by_type_id_and_entity_id(type_id, entity_id)

    def remove_entity_type_and_its_instances(self, type_id: int) -> None:
        if type_id not in self.__type_id_to_component_classes_names.keys():
            raise ValueError()

        for entity_id in self.__type_id_to_entities_ids[type_id]:
            del self.__id_to_entity[entity_id]

        for compo_class_name in self.__type_id_to_component_classes_names[type_id]:
            for entity_id in self.__type_id_to_entities_ids[type_id]:
                self.__component_class_name_to_entities_ids[compo_class_name].remove(entity_id)

        self.__component_class_name_to_entities_ids = {compo_class_name: ids_list for compo_class_name, ids_list in
                                                       self.__component_class_name_to_entities_ids.items() if ids_list}

        del self.__type_id_to_entities_ids[type_id]
        del self.__type_id_to_component_classes_names[type_id]


def get_component_of_entity(entity: List[Component], component_class: Type[Component]) -> Any:
    for component in entity:
        if isinstance(component, component_class):
            return component
