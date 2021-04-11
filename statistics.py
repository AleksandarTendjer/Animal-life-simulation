from threading import Thread
from time import time, sleep
from animal import Sex
import pygame_menu as pyMenu
import pygame
import sys
import xlwt
import matplotlib.pyplot as plt
from datetime import datetime


TRACKER_TIMEOUT = 3


class Stats:
    """Top level class holding multiple Trackers"""

    def __init__(self, world):
        """
        Initializes the Stats

        Args:
                world (World): The world
        """
        self.world = world
        self.trackers = [
            RabbitAvgTracker(world),
            FoxAvgTracker(world),
            FoodAvgTracker(world),
        ]
        self.element = dict()

    def start_all(self) -> None:
        """
        Starts all threads in the clump
        """

        for thread in self.trackers:
            thread.start()

    def join_all(self) -> None:
        """
        Join all threads in the clump
        """

        for thread in self.trackers:
            thread.join()

    def menu_show(self):
        menu = pyMenu.Menu(
            600, 600, "Simulation data analysis", theme=pyMenu.themes.THEME_SOLARIZED
        )
        menu.add.dropselect(
            "Statistics for feature :",
            [("speed", 1), ("hunger", 2), ("thirst", 3), ("size", 4), ("count", 5)],
            onchange=self.set_element,
        )
        menu.add.button("Draw statistics for feature", self.draw_graph)
        menu.add.button("Excel Export", self.output_Excel)
        menu.add.button("Exit", self.exit)
        menu.mainloop(self.world.screen)

    def exit(self):
        pyMenu.events.EXIT
        pygame.quit()
        sys.exit(0)

    def set_element(self, value, number):
        self.element = dict(val=value, num=number)
        print("value is: ")
        print(value)

    def draw_graph(self):

        if self.element["val"][0][0] == "speed":
            plt.plot(
                self.trackers[0].speed_avg, self.trackers[0].x, "-b", label="rabbit"
            )
            plt.plot(self.trackers[1].speed_avg, self.trackers[1].x, "-r", label="fox")
        elif self.element["val"][0][0] == "hunger":
            plt.plot(
                self.trackers[0].hunger_avg, self.trackers[0].x, "-b", label="rabbit"
            )
            plt.plot(self.trackers[1].hunger_avg, self.trackers[1].x, "-r", label="fox")
        elif self.element["val"][0][0] == "thirst":
            plt.plot(
                self.trackers[0].thirst_avg, self.trackers[0].x, "-b", label="rabbit"
            )
            plt.plot(self.trackers[1].thirst_avg, self.trackers[1].x, "-r", label="fox")
        elif self.element["val"][0][0] == "size":
            plt.plot(
                self.trackers[0].size_avg, self.trackers[0].x, "-b", label="rabbit"
            )
            plt.plot(self.trackers[1].size_avg, self.trackers[1].x, "-r", label="fox")
        elif self.element["val"][0][0] == "count":
            plt.plot(self.trackers[0].y, self.trackers[0].x, "-b", label="rabbit")
            plt.plot(self.trackers[1].y, self.trackers[1].x, "-r", label="fox")

        # naming the x axis
        plt.xlabel("time")
        # naming the y axis
        plt.ylabel(self.element["val"][0][0])

        # giving a title to my graph
        plt.title(self.element["val"][0][0] + " time")

        # function to show the plot
        plt.show()

    def output_Excel(self):
        # Specifying style
        workbook = xlwt.Workbook()
        now = datetime.now()
        current_time = now.strftime("%H%M%S")

        sheet = workbook.add_sheet("Analysis_food")

        style = xlwt.easyxf("font: bold 1")
        sheet.write(0, 0, self.trackers[2].title)
        sheet.write(0, 1, "time")

        for i in range(0, len(self.trackers[2].x)):
            sheet.write(i + 1, 1, self.trackers[2].x[i])
            sheet.write(i + 1, 0, self.trackers[2].y[i])

        workbook.save("analysis_food" + current_time + ".xls")

        sheet = workbook.add_sheet("Analysis_fox")
        style = xlwt.easyxf("font: bold 1")

        sheet.write(0, 0, "time")
        sheet.write(0, 1, self.trackers[1].title)
        sheet.write(0, 2, "speed avg")
        sheet.write(0, 3, "thirst avg")
        sheet.write(0, 4, "hunger avg")
        sheet.write(0, 5, "male count avg")
        sheet.write(0, 6, "female count avg")

        for i in range(0, len(self.trackers[1].x)):
            sheet.write(i + 1, 0, self.trackers[1].x[i])
            sheet.write(i + 1, 1, self.trackers[1].y[i])
            sheet.write(i + 1, 2, self.trackers[1].speed_avg[i])
            sheet.write(i + 1, 3, self.trackers[1].thirst_avg[i])
            sheet.write(i + 1, 4, self.trackers[1].hunger_avg[i])
            sheet.write(i + 1, 5, self.trackers[1].male_count[i])
            sheet.write(i + 1, 6, self.trackers[1].female_count[i])

        workbook.save("analysis_fox" + current_time + ".xls")

        sheet = workbook.add_sheet("Analysis_rabbit")
        style = xlwt.easyxf("font: bold 1")

        # rabbit
        sheet.write(0, 0, "time")
        sheet.write(0, 1, self.trackers[0].title)
        sheet.write(0, 2, "speed avg")
        sheet.write(0, 3, "thirst avg")
        sheet.write(0, 4, "hunger avg")
        sheet.write(0, 5, "male count avg")
        sheet.write(0, 6, "female count avg")

        for i in range(0, len(self.trackers[0].x)):
            sheet.write(i + 1, 0, self.trackers[0].x[i])
            sheet.write(i + 1, 1, self.trackers[0].y[i])
            sheet.write(i + 1, 2, self.trackers[0].speed_avg[i])
            sheet.write(i + 1, 3, self.trackers[0].thirst_avg[i])
            sheet.write(i + 1, 4, self.trackers[0].hunger_avg[i])
            sheet.write(i + 1, 5, self.trackers[0].male_count[i])
            sheet.write(i + 1, 6, self.trackers[0].female_count[i])
        workbook.save("analysis_rabbit" + current_time + ".xls")


class _Tracker(Thread):
    """Parent Tracker class"""

    def __init__(self, world, title: str, ylabel: str):

        Thread.__init__(self)

        self.world = world
        self.title = title
        self.ylabel = ylabel
        self.hunger_avg = []
        self.thirst_avg = []
        self.speed_avg = []
        self.size_avg = []
        self.female_count = []
        self.male_count = []

        self._last_time = time()
        # time
        self.x = []
        self.y = []

    def run(self) -> Exception:

        raise NotImplementedError()

    def _timeout(self) -> bool:

        return time() - self._last_time > TRACKER_TIMEOUT


class RabbitAvgTracker(_Tracker):
    """Tracker for Rabbit count"""

    def __init__(self, world):

        _Tracker.__init__(self, world, "Rabbit Count", "Rabbits")

    def run(self) -> None:
        """
        Collects the Rabbit count at the runtime
        """

        self.x.append(self.world.runtime / 1000)
        self.y.append(len(self.world.rabbits))
        last_count = len(self.world.rabbits)

        self.male_count.append(0)
        self.female_count.append(0)
        sum_hunger = 0
        sum_thirst = 0
        sum_speed = 0
        sum_size = 0
        male_count = 0
        female_count = 0
        self.hunger_avg.append(sum_hunger / last_count)
        self.thirst_avg.append(sum_thirst / last_count)
        self.speed_avg.append(sum_speed / last_count)
        self.size_avg.append(sum_size / last_count)

        while self.world.running:
            if len(self.world.rabbits) != last_count or self._timeout():
                self._last_time = time()
                last_count = len(self.world.rabbits)

                self.x.append(self.world.runtime / 1000)
                self.y.append(last_count)
                sum_hunger = 0
                sum_thirst = 0
                sum_speed = 0
                sum_size = 0
                male_count = 0
                female_count = 0
                for rabbit in self.world.rabbits:
                    sum_hunger += rabbit.hunger
                    sum_thirst += rabbit.thirst
                    sum_speed += rabbit.speed
                    sum_size += rabbit.size

                    if rabbit.sex == Sex.MALE:
                        male_count += 1
                    else:
                        female_count += 1
                self.male_count.append(male_count)
                self.female_count.append(female_count)
                self.hunger_avg.append(sum_hunger / last_count)
                self.thirst_avg.append(sum_thirst / last_count)
                self.speed_avg.append(sum_speed / last_count)
                self.size_avg.append(sum_size / last_count)
            sleep(1)


class FoodAvgTracker(_Tracker):
    """Tracker for Food count"""

    def __init__(self, world):

        _Tracker.__init__(self, world, "Food Count", "Food")

    def run(self) -> None:

        self.x.append(self.world.runtime / 1000)
        self.y.append(len(self.world.food))
        last_count = len(self.world.food)

        while self.world.running:
            if len(self.world.food) != last_count or self._timeout():
                self._last_time = time()
                last_count = len(self.world.food)

                self.x.append(self.world.runtime / 1000)
                self.y.append(len(self.world.food))

            sleep(1)


class FoxAvgTracker(_Tracker):
    """Tracker for Fox count"""

    def __init__(self, world):

        _Tracker.__init__(self, world, "Fox Count", "Foxes")

    def run(self) -> None:
        last_count = len(self.world.foxes)

        self.x.append(self.world.runtime / 1000)
        self.y.append(last_count)

        self.male_count.append(0)
        self.female_count.append(0)
        sum_hunger = 0
        sum_thirst = 0
        sum_speed = 0
        sum_size = 0
        male_count = 0
        female_count = 0
        self.hunger_avg.append(sum_hunger / last_count)
        self.thirst_avg.append(sum_thirst / last_count)
        self.speed_avg.append(sum_speed / last_count)
        self.size_avg.append(sum_size / last_count)

        last_count = len(self.world.foxes)

        while self.world.running:
            if len(self.world.foxes) != last_count or self._timeout():
                self._last_time = time()
                last_count = len(self.world.foxes)

                self.x.append(self.world.runtime / 1000)
                self.y.append(len(self.world.foxes))
                sum_hunger = 0
                sum_thirst = 0
                sum_speed = 0
                sum_size = 0
                male_count = 0
                female_count = 0
                for fox in self.world.foxes:
                    sum_hunger += fox.hunger
                    sum_thirst += fox.thirst
                    sum_speed += fox.speed
                    sum_size += fox.size
                    if fox.sex == Sex.MALE:
                        male_count += 1
                    else:
                        female_count += 1
                self.male_count.append(male_count)
                self.female_count.append(female_count)
                self.hunger_avg.append(sum_hunger / last_count)
                self.thirst_avg.append(sum_thirst / last_count)
                self.speed_avg.append(sum_speed / last_count)
                self.size_avg.append(sum_size / last_count)
            sleep(1)
