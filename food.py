import pygame

FOOD_IMAGE = pygame.image.load("clover.png")
FOOD_SIZE = 20
FOOD_IMAGE = pygame.transform.scale(FOOD_IMAGE, (FOOD_SIZE, FOOD_SIZE))


class Food:
    """Class representing Food in the world"""

    def __init__(self, world, pos: (float, float)):
        self.world = world
        self.pos = pos

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draws Rabbit to the screen

        Args:
                screen (pygame.Surface): The pygame surface
        """
        screen.blit(
            FOOD_IMAGE, (self.pos[0] - FOOD_SIZE / 2, self.pos[1] - FOOD_SIZE / 2)
        )
