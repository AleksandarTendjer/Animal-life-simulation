import pygame
import statistics
from worldtools import *
from math import sin, cos, atan2, pi
from random import uniform

from animal import State, Animal

RABBIT_IMAGE = pygame.image.load("rabbit.png")
RABBIT_SIZE = 30
RABBIT_IMAGE = pygame.transform.scale(RABBIT_IMAGE, (RABBIT_SIZE, RABBIT_SIZE))
tolerance=0.1

class Rabbit(Animal):
	"""Class representing a Rabbit in the world"""

	def __init__(self, world, pos: (float, float), speed: float):
		"""
		Initializes the Rabbit

		Args:
			world (World): The world
			pos ( (float, float) ): Starting position
			speed (float): Rabbit speed
		"""
		
		Animal.__init__(self, world, pos, speed)
		self.sight = 150
	
	def move(self) -> None:
		"""
		Moves Rabbit based on state
		1) If a fox is nearby, prioritize moving away
		2) If roaming, move to food or move randomly
		3) If reproducing, move towards another reproducing Rabbit
		"""

		# Generate all entities in sight
		foodlist, rabbitlist, foxlist,waterlist = self.sight_entities()

		# Check if any foxes nearby
		if foxlist:
			# Average point of all nearby foxes
			avgpoint = (
				sum([w.pos[0] for w in foxlist]) / len(foxlist),
				sum([w.pos[1] for w in foxlist]) / len(foxlist)
			)

			# Angle opposite from Rabbit to average point
			t = atan2(avgpoint[1] - self.pos[1], avgpoint[0] - self.pos[0]) + pi

			# Proposed move
			new_x = self.pos[0] + (self.speed * cos(t))
			new_y = self.pos[1] + (self.speed * sin(t))

			# Check if valid move
			if not self.world.in_bounds((new_x, new_y)):
				# Move towards center of world
				t = atan2(self.world.size[0]/2 - self.pos[1], self.world.size[1]/2 - self.pos[0])
				new_x = self.pos[0] + (self.speed * cos(t))
				new_y = self.pos[1] + (self.speed * sin(t))

			# Confirm move
			self.pos = (
				new_x,
				new_y
			)
		elif self.state == State.ROAM or self.hunger <= 50:
			# Find closest Food
			if foodlist:
				self.target = foodlist[0]

			# Check if target still exists
			if (self.target is not None) and (self.target in self.world.food):
				dist_to_target = distance(self.pos, self.target.pos)

				# Jump directly to Food if possible
				if dist_to_target <= self.speed:
					self.pos = self.target.pos
					self.world.food.remove(self.target)
					self.target = None

					self.eat(30)
					# Change state to REPRODUCE if Rabbit ate 2 Food
					if self.eat_count % 2 == 0 and self.eat_count != self._food_checkpoint:
						self._food_checkpoint_checkpoint = self.eat_count
						self.state = State.REPRODUCE
				# Take intermediate steps to food
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
			# Find closest Rabbit that is also REPRODUCE
			if rabbitlist:
				for r in rabbitlist:
					if r.state == State.REPRODUCE and r.sex!=self.sex:
						self.target = r
						break
			
			# Check if target still exists
			if (self.target is not None) and (self.target in self.world.rabbits):
				dist_to_target = distance(self.pos, self.target.pos)

				# Jump directly to partner if possible
				if dist_to_target <= self.speed:
					self.pos = self.target.pos
					# Add new Rabbit to world with variance of speed and possibility of mutation
					#if(uniform(0,1.0)<tolerance):
					#	mean_val=statistics.mean([self.speed, self.target.speed])
					#	mutation=mean_val+uniform(0.0,0.20)
					#	print("mutation")
					#	self.world.foxes.append(Rabbit(self.world, self.pos, mutation))
					#else:	
					self.world.rabbits.append(Rabbit(self.world, self.pos, variance(self.speed, self.target.speed, 1.0)))
					
					# Reset state to ROAM
					self.state = State.ROAM
					self.target.state = State.ROAM
					self.target = None
				# Take intermediate steps to Rabbit
				else:
					ratio = self.speed / dist_to_target
					self.pos = (
						self.pos[0] + ((self.target.pos[0] - self.pos[0]) * ratio),
						self.pos[1] + ((self.target.pos[1] - self.pos[1]) * ratio)
						)
			elif self.state==State.ROAM or self.thirst<=50:
				# Find closest water
				if waterlist:
					self.target = waterlist[0]
				
				dist_to_target = distance(self.pos, self.target.pos)
				# Jump directly to Food if possible
				if dist_to_target <= self.speed:
					self.pos = self.target.pos
					#]self.world.food.remove(self.target)
					self.target = None
					self.drink(30)
				# Change state to REPRODUCE if Rabbit drank 2 times
					if self.drink_count % 2 == 0 and self.drink_count != self._water_checkpoint:
						self._drink_checkpoint_checkpoint = self.drink_count
						self.state = State.REPRODUCE
				# Take intermediate steps to water
				else:
					ratio = self.speed / dist_to_target
					self.pos = (
						self.pos[0] + ((self.target.pos[0] - self.pos[0]) * ratio),
						self.pos[1] + ((self.target.pos[1] - self.pos[1]) * ratio)
						)
				
			else:
				self.roam_move()
		
		# Calculate hunger after movement
		self.hunger -= self.size#0.25
		# Calculate thirst after movement
		self.thirst -= self.speed*0.1#0.40
		if self.hunger <= 0 or self.thirst<=0:
			self.world.rabbits.remove(self)

		
				
	def draw(self, screen: pygame.Surface) -> None:
		"""
		Draws Rabbit to the screen

		Args:
			screen (pygame.Surface): The pygame surface
		"""
		sc_factor=round(self.size*RABBIT_SIZE)
		rabbit_im= pygame.transform.scale(RABBIT_IMAGE, (sc_factor,sc_factor))
		screen.blit(rabbit_im, (self.pos[0] - RABBIT_SIZE/2, self.pos[1] - RABBIT_SIZE/2))