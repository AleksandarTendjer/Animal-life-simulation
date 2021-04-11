from random import random, randint, choice
import sys
from noise import pnoise2
import json
from PIL import ImageDraw
from PIL import Image

from enum import Enum


class NoiseMapBiome(Enum):
    OCEAN = 1
    SHALLOWS = 2
    BEACH = 3
    TUNDRA = 6
    GRASSLAND = 9
    FOREST = 10
    SNOW = 15
    TAIGA = 16
    SWAMP = 17


class Cell:
    def __init__(self, x, y, noise_value):
        self.x = x
        self.y = y
        self.noise_value = noise_value
        self.biome = None

    def __iter__(self):
        """ Yields a dictionary when dict() is called for serializing to JSON """
        yield "x", self.x
        yield "y", self.y
        yield "noise_value", self.noise_value
        yield "biome", self.biome


class NoiseWidth:
    """
    Defines where a range begins and ends.

    Also contains a helpful name tag eg. water, mountain, etc.
    """

    def __init__(self, name, threshold):
        self.name = name
        self.threshold = threshold

    def __iter__(self):
        """ Yields a dictionary when dict() is called for serializing to JSON """
        yield "name", self.name
        yield "threshold", self.threshold


class Map2D:
    def __init__(self, width, height, noise_ranges=[], cells=[], moisture_map=None):

        self.width = width
        self.height = height
        self.noise_ranges = noise_ranges
        self.cells = cells
        self.moisture_map = moisture_map
        self.scale = None
        self.octaves = None
        self.image = None
        self.waterlist = []

        # create a dictionary from the noise ranges list for quick lookups later
        self.noise_range_dict = {}
        for noise_range in noise_ranges:
            self.noise_range_dict[noise_range.name] = noise_range

    def generate(
        self, scale, octaves, persistence=0.5, lacunarity=2.0, sink_edges=False
    ):
        """
        Generates the noise map.
        :param scale: it's the scale of the map. Higher = zoomed in, lower = zoomed out.
        :param octaves: the level of detail. Lower = more peaks and valleys, higher = less peaks and valleys.
        :param persistence: how much an octave contributes to overall shape (adjusts amplitude).
        :param lacunarity: the level of detail on each octave (adjusts frequency).
        :param sink_edges: Sinks the edges and corners of the map into the ocean to create islands.
        """
        self.scale = scale
        self.octaves = octaves

        self.cells = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                noise_value = None
                noise_value = pnoise2(
                    x=x / scale,
                    y=y / scale,
                    octaves=octaves,
                    persistence=persistence,
                    lacunarity=lacunarity,
                )
                row += [Cell(x, y, noise_value)]
            self.cells += row

    def biome(self, elevation, moisture):
        """ Determine the biome from the elevation & moisture of the cell """

        """ Water/Shore"""
        if elevation <= self.noise_range_dict["water"].threshold:
            return NoiseMapBiome.OCEAN

        if elevation <= self.noise_range_dict["sand"].threshold and moisture >= 0.2:
            return NoiseMapBiome.SWAMP

        if elevation <= self.noise_range_dict["shallowwater"].threshold:
            return NoiseMapBiome.SHALLOWS
        if elevation <= self.noise_range_dict["sand"].threshold:
            return NoiseMapBiome.BEACH

        """ High mountain """
        if elevation > self.noise_range_dict["hugemountain"].threshold:
            if moisture < 0.1:
                return NoiseMapBiome.SCORCHED
            elif moisture < 0.2:
                return NoiseMapBiome.BARE
            elif moisture < 0.5:
                return NoiseMapBiome.TUNDRA
            return NoiseMapBiome.SNOW

        """ Mountain """
        if elevation > self.noise_range_dict["mountain"].threshold:
            if moisture < 0.66:
                return NoiseMapBiome.SHRUBLAND
            return NoiseMapBiome.TAIGA

        """ Land """
        if moisture < 0.33:
            return NoiseMapBiome.GRASSLAND
        return NoiseMapBiome.FOREST

    def __iter__(self):
        """ Yields a dictionary when dict() is called for serializing to JSON """
        yield "width", self.width
        yield "height", self.height
        yield "scale", self.scale
        yield "octaves", self.octaves
        yield "noise_ranges", [dict(noise_range) for noise_range in self.noise_ranges]
        yield "cells", [dict(cell) for cell in self.cells]
        if self.moisture_map is not None:
            yield "moisture_map", dict(self.moisture_map)

    def display_as_image(self, cell_size):
        """
        Display the map as an image.

        :param cell_size: The size of each cell.
        :return: None

        """
        # add some extra height to the image for the legend
        legend_height = 200
        legend_width = 1500
        image_width = self.width * cell_size
        if image_width < legend_width:
            image_width = legend_width
        self.image = Image.new(
            "RGBA",
            size=(image_width, (self.height * cell_size) + legend_height),
            color=(0, 0, 0),
        )

        d = ImageDraw.Draw(self.image)
        for cell_index in range(len(self.cells)):
            # get cells
            cell = self.cells[cell_index]
            moisture_cell = self.moisture_map.cells[cell_index]
            cell.biome = self.biome(cell.noise_value, moisture_cell.noise_value)
            biome_color = self.get_biome_color(cell.biome)
            d.rectangle(
                [
                    cell.x * cell_size,
                    cell.y * cell_size,
                    cell.x * cell_size + cell_size,
                    cell.y * cell_size + cell_size,
                ],
                fill=biome_color,
            )

        # self.image.show()

    def chunks(self, target_list, chunk_size):
        """
        Break a big list into smaller lists.
        """
        for i in range(0, len(target_list), chunk_size):
            yield target_list[i : i + chunk_size]

    def get_biome_color(self, value):
        if value == NoiseMapBiome.OCEAN:
            return (54, 62, 150)  # dark blue
        elif value == NoiseMapBiome.SHALLOWS:
            return (88, 205, 237)  # cyan
        elif value == NoiseMapBiome.BEACH:
            return (247, 247, 119)  # yellow
        elif value == NoiseMapBiome.TUNDRA:
            return (132, 173, 158)  # grey green
        elif value == NoiseMapBiome.GRASSLAND:
            return (55, 181, 43)  # green
        elif value == NoiseMapBiome.FOREST:
            return (1, 50, 32)  # green black
        elif value == NoiseMapBiome.SNOW:
            return (255, 255, 255)  # white
        elif value == NoiseMapBiome.TAIGA:
            return (62, 87, 71)  # dark olive
        elif value == NoiseMapBiome.SWAMP:
            return (92, 112, 104)  # grey green
        else:
            return (0, 0, 0)  # black

    def ret_water_points(self):
        for cell_index in range(len(self.cells)):
            # get cells
            cell = self.cells[cell_index]
            moisture_cell = self.moisture_map.cells[cell_index]
            cell.biome = self.biome(cell.noise_value, moisture_cell.noise_value)

    def save(self, file_name):
        """ Save the map as JSON to a file. """
        with open(file_name, "w", encoding="utf8") as file:
            json.dump(dict(self), file, indent=4)
            file.close()

    def save_image(self, file_name):
        """ Save the map image file. """
        if self.image is not None:
            self.image.save(file_name)

    @classmethod
    def load(cls, data) -> "NoiseMap":
        if data is not None:
            # parse map info
            width = data["width"]
            height = data["height"]

            # parse cells
            cells = [
                Cell(cell["x"], cell["y"], cell["noise_value"])
                for cell in data["cells"]
            ]

            # parse noise ranges
            noise_ranges = [
                NoiseWidth(noise_range["name"], noise_range["threshold"])
                for noise_range in data["noise_ranges"]
            ]

            # parse moisture map
            moisture_map = None
            if "moisture_map" in data:
                moisture_map = Map2D.load(data["moisture_map"])

            return cls(width, height, noise_ranges, cells, moisture_map)
