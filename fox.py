import pygame
from worldtools import *
from animal import State, Animal
import statistics
from math import sin, cos, pi
from random import uniform

WOLF_IMAGE = pygame.image.load("fox.png")
WOLF_SIZE = 30
WOLF_IMAGE = pygame.transform.scale(WOLF_IMAGE, (WOLF_SIZE, WOLF_SIZE))
tolerance=0.1

class Fox(Animal):
	"""Class representing a Fox in the world"""

	def __init__(self, world, pos: (float, float), speed: float):
		"""
		Initializes the Fox

		Args:
			world (World): The world
			pos ( (float, float) ): Starting position
			speed (float): Fox speed
		"""
		
		Animal.__init__(self, world, pos, speed)
		self.sight = 200

	def move(self):
		"""
		Moves Fox based on state
		1) If roaming, move to Rabbit or move randomly
		2) If reproducing, move towards another reproducing Fox
		"""

		# Generate all entities in sight
		foodlist, rabbitlist, foxlist = self.sight_entities()

		if self.state == State.ROAM or self.hunger <= 50:
			# Find closest Rabbit
			if rabbitlist:
				self.target = rabbitlist[0]

			# Check if target still exists
			if (self.target is not None) and (self.target in self.world.rabbits):
				dist_to_target = distance(self.pos, self.target.pos)

				# Jump directly to Rabbit if possible
				if dist_to_target <= self.speed:
					self.pos = self.target.pos
					self.world.rabbits.remove(self.target)
					self.target = None
				
					self.eat(30)

					# Change state to REPRODUCE if Fox ate 3 Rabbit
					if self.eat_count % 3 == 0 and self.eat_count != self._food_checkpoint:
						self._food_checkpoint_checkpoint = self.eat_count
						self.state = State.REPRODUCE
				# Take intermediate steps to Rabbit
				else:
					ratio = self.speed / dist_to_target
					self.pos = (
						self.pos[0] + ((self.target.pos[0] - self.pos[0]) * ratio),
						self.pos[1] + ((self.target.pos[1] - self.pos[1]) * ratio)
					)
			# Make a random movement towards movement angle
			else:
				self.roam_move()
		elif self.state == State.REPRODUCE:
			# Find closest Fox that is also REPRODUCE
			if foxlist:
				for w in foxlist:
					if w.state == State.REPRODUCE:
						self.target = w
						break
			
			# Check if target still exists
			if (self.target is not None) and (self.target in self.world.foxes):
				dist_to_target = distance(self.pos, self.target.pos)

				# Jump directly to partner if possible
				if dist_to_target <= self.speed:
					self.pos = self.target.pos
					# Add new Fox to world with variance of speed and possibility of mutation
					#if(uniform(0,1.0)<tolerance):
					#	mean_val=statistics.mean([self.speed, self.target.speed])
					#	print("mutation fox")
					#	mutation=mean_val+uniform(0.0,0.20)
					#	self.world.foxes.append(Fox(self.world, self.pos, mutation))
					#else:	
					self.world.foxes.append(Fox(self.world, self.pos, variance(self.speed, self.target.speed, 1.0)))
					
					# Reset state to ROAM
					self.state = State.ROAM
					self.target.state = State.ROAM
					self.target = None
				# Take intermediate steps to Fox
				else:
					ratio = self.speed / dist_to_target
					self.pos = (
						self.pos[0] + ((self.target.pos[0] - self.pos[0]) * ratio),
						self.pos[1] + ((self.target.pos[1] - self.pos[1]) * ratio)
						)
			else:
				self.roam_move()
		
		# Calculate hunger after movement
		self.hunger -= 0.25
		if self.hunger <= 0:
			self.world.foxes.remove(self)

	def draw(self, screen: pygame.Surface):
		"""
		Draws Fox to the screen

		Args:
			screen (pygame.Surface): The pygame surface
		"""
		screen.blit(WOLF_IMAGE, (self.pos[0] - WOLF_SIZE/2, self.pos[1] - WOLF_SIZE/2))