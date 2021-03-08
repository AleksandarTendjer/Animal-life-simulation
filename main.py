import sys
import pygame
from world import World
from simstats import StatClump
import os
import argparse
from terrain_gen import NoiseWidth
from terrain_gen import Map2D

import matplotlib.pyplot as plt

#DEFAULT_SCREEN_SIZE = (800, 600)
DEFAULT_SCREEN_SIZE = (960, 750)
# DEFAULT_SCREEN_SIZE = (1280, 720)
#BG_IMG = pygame.image.load("bg.jpg")


if __name__ == "__main__":
		# generate
	# create parser
	parser = argparse.ArgumentParser()
	
	# add arguments to the parser
	parser.add_argument('--water', help="Height level of the water", type=float, default=0.0)
	parser.add_argument('--shallowwater', help="Height level of the shallow water", type=float, default=0.05)
	parser.add_argument('--sand', help="Height level of the sand", type=float, default=0.1)
	parser.add_argument('--land', help="Height of normal grass/land/forest", type=float, default=0.6)
	parser.add_argument('--mountain', help="Height of mountains", type=float, default=0.5)
	parser.add_argument('--hugemountain', help="Height of huge mountains", type=float, default=0.6)
	
	parser.add_argument('--scale', help="Higher=zoomed in, Lower=zoomed out.", type=float, default=200)
	parser.add_argument('--persistence', help="how much an octave contributes to overall shape (adjusts amplitude).",type=float, default=0.5)
	parser.add_argument('--lacunarity', help="The level of detail on each octave (adjusts frequency).", type=float,
                        default=3.0)
	
	parser.add_argument('--moistureo', help="Moisture octaves.", type=int, default=8)
	parser.add_argument('--moistures', help="Moisture scale.", type=float, default=200)
	parser.add_argument('--moisturep', help="Moisture persistence.", type=float, default=0.5)
	parser.add_argument('--moisturel', help="Moisture lacunarity.", type=float, default=3.0)
	parser.add_argument('--octaves', help="Octaves used for generation.", type=int, default=8)

# parse the arguments
	args = parser.parse_args()
	
	scale = args.scale
	moisture_scale = args.moistures

	noise_ranges = [
		NoiseWidth('hugemountain', args.hugemountain),
		NoiseWidth('mountain', args.mountain),
		NoiseWidth('land', args.land),
		NoiseWidth('sand', args.sand),
		NoiseWidth('shallowwater', args.shallowwater),
		NoiseWidth('water', args.water),
	]
	# generate terrain
	noise_map = Map2D(DEFAULT_SCREEN_SIZE[0], DEFAULT_SCREEN_SIZE[1], noise_ranges)
	noise_map.generate( scale, args.octaves, args.persistence, args.lacunarity)

	# generate moisture
	moisture_map = Map2D(DEFAULT_SCREEN_SIZE[0], DEFAULT_SCREEN_SIZE[1])
	moisture_map.generate(moisture_scale, args.moistureo, args.moisturep, args.moisturel)

	noise_map.moisture_map = moisture_map
	
	# display map
	tilesize=7
	#noise_map.display_as_image(tilesize)
	file_name = 'noise_map'
	noise_map.save_image(file_name+'.png') # save the png too
	
	noise_map.ret_water_points()
	
	BG_IMG = pygame.image.load(file_name+'.png')
	# Start pygame
	pygame.init()

	# pygame screen and timer
	screen = pygame.display.set_mode(DEFAULT_SCREEN_SIZE)
	clock = pygame.time.Clock()

	# Create world
	world = World(DEFAULT_SCREEN_SIZE, clock, screen,noise_map.cells)
	paused = False

	# Create Trackers 
	sc = StatClump(world)
	sc.start_all()

	# Main pygame loop
	while 1:
		# Pause check
		if not paused:
			world.step()
			pygame.display.flip()
			screen.fill((0, 0, 0))
			screen.blit(BG_IMG, [0, 0])

		# pygame event handler
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				world.running = False
				break
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					paused = not paused

		# Exit condition
		if not world.running:
			break

		# FPS control
		clock.tick(30)

	# Exit pygame
	pygame.quit()

	# join all Trackers
	sc.join_all()

	# Create pyplot environment
	fig, axes = plt.subplots(3, 2)
	fig.canvas.set_window_title("Evolution Simulation Results")

	# Place Trackers
	sc.trackers[0].plot(axes[0, 0])	# Rabbit Count
	sc.trackers[1].plot(axes[1, 0])	# Fox Count
	sc.trackers[2].plot(axes[2, 0])	# Food Count
	sc.trackers[3].plot(axes[0, 1])	# Rabbit Speed
	sc.trackers[4].plot(axes[1, 1]) # Fox Speed
	fig.delaxes(axes[2, 1])			# Temp delete

	# Show pyplot results
	fig.tight_layout()
	plt.show()

	print("Simulation Finished")
	sys.exit(0)


