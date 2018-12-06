[![license](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/avikor/entity_component_system/blob/master/LICENSE)
[![Python Versions](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue.svg)](https://www.python.org/downloads/release/python-350/)
[![Build Status](https://travis-ci.org/avikor/constraint_satisfaction_problems.svg?branch=master)](https://travis-ci.org/avikor/entity_component_system)
[![Code Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](https://codecov.io/gh/avikor/entity_component_system)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-brightgreen.svg)](https://app.codacy.com/project/avikor/entity_component_system/dashboard)
[![Pygame](https://i.imgur.com/DN3bO38.png)](https://www.pygame.org/news)

## Aliens Game
This repository stores an Entity-Component-System implementation of the Aliens game using the [pygame library](https://www.pygame.org).  
The Aliens game was first implemented as a pygame-library game-example.  
The original source code of the game can be viewed [here](https://github.com/xamox/pygame/blob/master/examples/aliens.py).  
  
A small bit of Aliens game play:  
  
[![Aliens Gameplay](https://i.imgur.com/Z7Z2t2k.png)](https://streamable.com/iye6w)

The ECS implementation of the Aliens game can be found at 'examples/aliens_game'.

## Entity Component System
**Entity–Component–System (ECS)** is an architectural pattern that is mostly used in game development.  
A **component** is a plain old data structure (POD), i.e. a data structure that is implemented only as passive  
collections of field values, without any methods.  
An **entity** is a container of  **components**.  
A **system** is a routine which implements some part of the game's logic, and is aware of both entities and components.  

#### A Toy Example
Say we wish to develop a two dimensional game in which an alien spaceship moves across the screen. Thus we would need a  
Graphics Component, which would store data concerning as to how to display the spaceship on screen.  
We would also need a Velocity Component which would store data regarding the spaceship's speed in both horizontal and vertical axis.  
We could store both components in a container which we would name a spaceship entity.  
Consequently we would also need to implement a draw and erase routines (systems), which could draw and erase the spaceship.  
And a mover system as well, which would move the spaceship according to its velocity.  
Now, should we want to implement yet another entity, say a plane, we could use our already implemented  
Graphics and Velocity and components, name a new plane entity, and use our current systems to move the plane around  
in the same way we move a spaceship, optionally by using a different velocity.   
Other than the plane entity, no new class or routine should be implemented.
  
Using traditional OOP design, we could've implemented an abstract GameObject class, and have each new class inherit it.    
Thus if we want a plane instance, which behaves a bit differently from an alien spaceship, we would've needed to implement a new plane class.  
Now say we wish to implement a graphic object which does not move, some of the approaches to solve this might include:
1. Instancing the object with zero horizontal and vertical speeds.
2. Removing the velocity logic from GameObject class, and implementing it only in the spaceship and plane classes.
3. Implementing a new abstract class which inherits from GameObject, that has velocity. We could name it MovableGameObject,
and have Spaceship and Plane classes inherit it. Thus violating Liskov substitution principle.
4. There are other solutions as well.
 
Yet ECS saves us all this trouble, all the while not using polymorphism and bloated inheritance trees, which should be avoided like the plague.  
If we want to define an entity which does not move, simply make a container of a single Graphics Component.  
In this fashion, ECS adheres to *composition over inheritance principle*, which allows greater flexibility in design.  

## Some Implementation details
Implemented components (which can be found at 'ecs/component.py'):  
1. GraphicComponent.
2. AnimationCycleComponent.
3. TextComponent.
4. VelocityComponent.
5. HorizontalOrientationComponent.
6. AudioComponent.
7. LifeTimeComponent

Implemented systems (which can be found at 'ecs/systems.py'):  
1. erase_system.
2. draw_system.
3. rotate_animation_cycle_system.
4. rewrite_text_system.
5. move_system.
6. move_screen_bounded_horizontally_oriented_entity_system.
7. collision_detection_system.
8. collision_detection_with_handling_system.
9. lists_collision_detection_system.
10. lists_collision_detection_with_handling_system.
11. decrease_lifetime_system.  

Additionally, an EntitiesManager class which stores all entities can be found at 'ecs/entities_manager.py'.     
This class allows for the definition of new types, instancing of new entities, and all sorts of getters and destructors  
to be used by various systems.  
Some of its methods include:
1. add_entity_type.
2. instantiate_entity.
3. get_all_entities_of_type.
4. get_all_entities_with_component_class.
5. get_all_instances_of_component_class.
6. remove_entity.
7. remove_entity_type_and_its_entities.

A 'type' is simply an integer which serves as a unique id, along with a list of the various components required to  
instantiate a new entity of the aforementioned 'type'. You can think of it as a class.  
Thus several types can be used to define entities which consist of the same components.  
For example, a spaceship type with graphics and velocity components, and a plane type which consists of of the same components, albeit using different instances of them.  
This allows us to move a plane differently than a spaceship (even if it has the same velocity of a spaceship), without  
having to implement a new class.   
Thus ECS adheres to the *DRY principle*.  