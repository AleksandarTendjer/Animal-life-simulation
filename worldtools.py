from math import sqrt
from random import uniform

def distance(pos1: (float, float), pos2: (float, float)) -> float:
	"""
	Calculates the Euclidean distance between two points

	Args:
		pos1 ( (float, float) ): Position 1
		pos2 ( (float, float) ): Position 2

	Returns:
		float: The distance between two points
	"""

	return sqrt(
		((pos2[0] - pos1[0])**2) +
		((pos2[1] - pos1[1])**2)
		)

def variance(val1: float, val2: float, variance: float) -> float:
	"""
	Calculates a variance between values with a spread.
	Adds half the variance to the average of the two values.

	Args:
		val1 (float): Value 1
		val2 (float): Value 2
		variance (float): The spread amount

	Returns:
		float: New value with variance added
	"""

	return ((val1 + val2) / 2) + uniform(-(variance/2), variance/2)

def contains(list: list , filter)->bool:
    for x in list:
        if filter(x):
            return True
    return False