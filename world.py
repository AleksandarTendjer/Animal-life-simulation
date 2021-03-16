import random
from worldtools import *
import pygame
from rabbit import Rabbit
from fox import Fox
from food import Food
from terrain_gen  import Map2D
from terrain_gen import Cell, NoiseMapBiome


class World():
	"""Class representing an environment"""

	def __init__(self, srn_sz: (float, float), clock: pygame.time.Clock, screen: pygame.Surface,allCells):
		"""
		Initializes the World

		Args:
			srn_sz ( (float, float) ): Screen size
			clock (pygame.time.Clock): pygame Clock
			screen (pygame.Surface): pygame Screen
		"""

		self.running = True

		self._clock = clock
		self.screen = screen
		
		self.runtime = 0
		self.runtime_checkpoint = 0

		self.size = srn_sz
		self.rabbits = []
		self.foxes = []
		self.food = []
		self.landcells=[]
		self.shorecells=[]
		self.watercells=[]
		self.cells=allCells
		self._classify_terrain()
		for _ in range(20):

			rand_pos=random.choice(self.landcells) 	
			self.rabbits.append(Rabbit(self, (rand_pos.x,rand_pos.y),self._random_speed() ))#2.5

		for _ in range(6):
			rand_pos=random.choice(self.landcells) 	
			self.foxes.append(Fox(self, (rand_pos.x,rand_pos.y), self._random_speed())) #3 self._random_pos()

		for _ in range(80):
			rand_pos=random.choice(self.landcells) 
			self.food.append(Food(self,(rand_pos.x,rand_pos.y))) #self._random_pos()

		
		self._update_screen()

	
	def step(self) -> None:
		"""
		Advances the world by one frame
		"""

		# Add food every time frame
		self.runtime += self._clock.get_time()
		if (self.runtime - self.runtime_checkpoint) / 1000 >= 1 and len(self.food) < 80:
			self.runtime_checkpoint = self.runtime
			rand_pos=random.choice(self.landcells) 
			self.food.append(Food(self,(rand_pos.x,rand_pos.y))) 
			
		# Move all animals
		for rabbit in self.rabbits:
			rabbit.move()
		for fox in self.foxes:
			fox.move()
		
		# Stop condition
		if self._end_condition():
			self.running = False
			return

		# Redraw all entities
		self._update_screen()
		
	def _update_screen(self) -> None:
		"""
		Draws all entities in the world to the screen
		"""

		for rabbit in self.rabbits:
			rabbit.draw(self.screen)

		for fox in self.foxes:
			fox.draw(self.screen)

		for food in self.food:
			food.draw(self.screen)
		
	def in_bounds(self, pos: (float, float)) -> bool:
		"""
		Determines if a position is valid in the world

		Args:
			pos ( (float, float) ): Position

		Returns:
			bool: True if pos is valid in the world, False otherwise
		"""
		
		return (
			0 <= pos[0] < self.size[0] and
			0 <= pos[1] < self.size[1]
			)

	def _end_condition(self) -> bool:
		"""
		Determines if the simulation is completed

		Returns:
			bool: True if the world is "complete", False otherwise
		"""

		return len(self.rabbits) <= 1 or len(self.foxes) <= 0
		# return len(self.rabbits) <= 0 or len(self.foxes) <= 0

	def _random_pos(self) -> (float, float):
		"""
		Returns a random position in the world

		Args:
			self (World): self

		Returns:
			(float, float): Tuple representing the position
		"""
		
		return (
			random.uniform(0, self.size[0]),
			random.uniform(0, self.size[1])
			)
	def _random_speed(self) -> ( float):
		"""
		Returns random speed of animal

		Args:
			self (World): self

		Returns:
			float: float value representing the speed
		"""
		
		return random.uniform(0,4.0)
			
			

	def __repr__(self) -> str:
		return "size={}, rabbits={}, foxes={}, food={}".format(
			self.size,
			len(self.rabbits),
			len(self.foxes),
			len(self.food)
		)

	
	def _classify_terrain(self):
		for cell in self.cells: 
			if cell.biome==NoiseMapBiome.FOREST or cell.biome==NoiseMapBiome.GRASSLAND:
				self.landcells.append(cell)
			elif cell.biome==NoiseMapBiome.SHALLOWS:
				self.shorecells.append(cell)
			elif cell.biome==NoiseMapBiome.OCEAN:
				self.watercells.append(cell)
		self.cells.clear()
	
		