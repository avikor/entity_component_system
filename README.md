## Aliens Game
This repository stores an Entity Component System implementation of the aliens game, first implemented as pygame library  
toy example. The original source code of the game can be view [here](https://github.com/xamox/pygame/blob/master/examples/aliens.py).  
  
Some Gameplay:  
  
[![Aliens Gameplay](https://i.imgur.com/Z7Z2t2k.png)](https://streamable.com/iye6w)


## Entity Component System
**Entity–Component–System (ECS)** is an architectural pattern that is mostly used in game development.  
A **component** is a plain old data structure (POD), i.e. a data structure that is implemented only as passive  
collections of field values, without any methods or other object oriented features.  
An **entity** is a container of  **components**.  
A **system** is a routine which implements some part of the game's logic, and is aware of entities and components.  

##### A Toy Example
Say we develop a two dimensional game in which an alien spaceship moves across the screen. Thus we would need a  
Graphics Component, which would hold data concerning as to how to display the spaceship on screen.  
We would also need a Velocity Component which would hold data regarding the spaceship's speed in both axis.  
We can store both of those components in a container which we would name a spaceship entity.  
Consequently we would also need to implement a draw and erase systems (routines), which could draw and erase the spaceship.  
As well as a mover system, which would move the spaceship.  
Now, should we want to implement another yet another entity, say a plane, we could use our already implemented  
Graphics and Velocity and components, name a new plane entity, and use our current systems to move the plane around.  
  
Using traditional OOP design, we could've implemented an abstract GameObject class, and have each new class / entity / type  
instance / whatever inherit GameObject.  
Say now we want to implement a graphic object which does not move, some of the approaches to solve this problem might include:
1. Instancing the object with zero horizontal and vertical speeds.
2. Removing the velocity logic from GameObject class, and implementing it only in the Spaceship and Plane classes.
3. Defining a new abstract class which inherits from GameObject, that has velocity. We could name it MovableGameObject,  
and have Spaceship and Plane classes inherit it.
4. There are other solutions of course...
 
Yet ECS saves us all this trouble, all the while not using polymorphism and inheritance, which should be avoided like the plague.  
If we want to define an entity which does not move, simply make a container of a single Graphics Component.  
Hence ECS adheres to composition over inheritance principle which allows greater flexibility in defining entities.  

## Some Implementation details
All implemented components could be found in 'component.py', similarly for systems and 'systems.py'.
'entities_manager.py' stores an EntitiesManager class, which holds all entities of a game.  
This class allows for the definitions of new types, instancing of new entities, and all sorts of getters and destructors.