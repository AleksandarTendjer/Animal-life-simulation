from worldtools import *
from enum import Enum
from math import sin, cos, pi
from random import uniform
from random import choice
from random import randint
import time

class State(Enum):
	ROAM = 0
	REPRODUCE = 1


class Sex(Enum):
	MALE = 0
	FEMALE = 1

class Animal:
	"""Class representing Animal in the world"""

	def __init__(self, world, pos: (float, float), speed: float):
		"""
		Initializes the Animal

		Args:
			world (World): The world
			pos ( (float, float) ): Starting position
			speed (float): Animal speed
			sex(SEX): Sex 
		"""

		self.speed = speed
		self.pos = pos
		self.world = world
		self.sex = choice(list(Sex))
		self.size=randint(5, 10)/10#uniform(0,1)
		# Movement variables
		self.target = None
		self.movement_angle = uniform(0, pi*2)

		# Food variables
		self.hunger = 100
		self.eat_count = 0
		self._food_checkpoint = 0
		# Thirst variables
		self.thirst = 100
		self.drink_count = 0
		self._water_checkpoint = 0

		# Set state
		self.state = State.ROAM
	
	def move(self) -> Exception:
		"""
		Moves an animal based on state

		Raises:
			NotImplementedError: Should be overwritten in a derived class

		Returns:
			Exception: Will always raise NotImplementedError if called from Animal class
		"""
		
		raise NotImplementedError()
		
	def draw(self, screen) -> Exception:
		"""
		Draws an animal to the screen

		Args:
			screen (pygame.screen): pygame screen

		Raises:
			NotImplementedError: Should be overwritten in a derived class

		Returns:
			Exception: Will always raise NotImplementedError if called from Animal class
		"""

		raise NotImplementedError()

	def sight_entities(self) -> (["Food"], ["Rabbit"], ["Fox"],["Water"]):
		"""
		Returns all entites in vision of the Animal

		Args:
			self (Animal): self

		Returns:
			([Food], [Rabbit], [Fox]): Returns a 3-tuple with Food, Rabbit, Fox in vision
		"""

		# Get foods around self
		foodlist = []
		for food in self.world.food:
			if self != food and self._in_sight(food):	foodlist.append(food)

		#get water around self 
		waterlist=[]
		#for water in self.world.watercells:
		#	water.pos=(water.x,water.y)
		#	if self!=water and self._in_sight(water): waterlist.append(water)
		for i in list(range(0,25)):
			water=choice(self.world.shorecells)
			water.pos=(water.x,water.y)
			waterlist.append(water)

		# Get rabbits around self
		rabbitlist = []
		for rabbit in self.world.rabbits:
			if self != rabbit and self._in_sight(rabbit): rabbitlist.append(rabbit)

		# Get foxes around self
		foxlist = []
		for fox in self.world.foxes:
			if self != fox and self._in_sight(fox):	foxlist.append(fox)
		# Get water around self
		#waterlist = []
		#for water in self.world.waters:
		#	if self != water and self._in_sight(water):	waterlist.append(water)

		# Sort by distance to self
		foodlist.sort(key=lambda x: distance(self.pos, x.pos))
		rabbitlist.sort(key=lambda x: distance(self.pos, x.pos))
		foxlist.sort(key=lambda x: distance(self.pos, x.pos))
		waterlist.sort(key=lambda x: distance(self.pos, x.pos))
		
		return (foodlist, rabbitlist, foxlist,waterlist) 
	
	def eat(self, inc: float) -> None:
		"""
		Increments eating food source and adds to hunger

		Args:
			inc (int): Amount to increase hunger
		"""

		# Increment eat count
		self.eat_count += 1

		# Limit to 100
		if self.hunger + inc >= 100:
			self.hunger = 100
		else:
			self.hunger += inc
	def drink(self, inc: float) -> None:
		"""
		Increments drinking water source and adds to thirst

		Args:
			inc (int): Amount to increase thirst
		"""
		
		# Increment eat count
		self.drink_count += 1
		#wait for half a sec
		self.stopwatch(0.5)
		# Limit to 100
		if self.thirst + inc >= 100:
			self.thirst = 100
		else:
			self.thirst += inc
	
	def roam_move(self) -> None:
		"""
		Moves Animal in the direction they are facing and slightly changes movement angle
		"""

		# Proposed move
		new_x = self.pos[0] + (self.speed * cos(self.movement_angle))
		new_y = self.pos[1] + (self.speed * sin(self.movement_angle))

		# Check if valid move
		while self.world.in_bounds((new_x, new_y))!=True and contains(self.world.watercells, lambda x: x.x == new_x and x.y ==new_y)!=True :  # list of all elements with .n==30
			
			# Reset move
			self.movement_angle += pi/2
			new_x = self.pos[0] + (self.speed * cos(self.movement_angle))
			new_y = self.pos[1] + (self.speed * sin(self.movement_angle))
			
		# Confirm move
		self.pos = (
			new_x,
			new_y
		)

		# Adjust movement angle
		self.movement_angle += uniform(-pi*2 / 36, pi*2 / 36)
		
	def _in_sight(self, entity) -> bool:
		"""
		Returns if an entity (which has a pos) is in sight of the Animal

		Args:
			entity (Animal or Food): Entity to check

		Returns:
			bool: True if entity is in sight, False otherwise
		"""
		
		return distance(self.pos, entity.pos) <= self.sight

	def __repr__(self) -> str:
		return "{}".format(self.pos)
		# return "speed={}, pos={}, hunger={}, state={}".format(
		# 	self.speed,
		# 	self.pos,
		# 	self.hunger,
		# 	self.state
		# )

	def stopwatch(self,seconds):
		start = time.time()
	#	time.clock()    
		elapsed = 0
		while elapsed < seconds:
			elapsed = time.time() - start
			#print "loop cycle time: %f, seconds count: %02d" % (time.clock() , elapsed) 
			#time.sleep(1)  

