from threading import Thread
from time import time, sleep

TRACKER_TIMEOUT = 3


class Stats:
    """Top level class holding multiple Trackers"""

    def __init__(self, world):
        """
        Initializes the Stats

        Args:
                world (World): The world
        """

        self.trackers = [
            RabbitCountTracker(world),
            FoxCountTracker(world),
            FoodCountTracker(world),
        ]

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


class _Tracker(Thread):
    """Parent Tracker class"""

    def __init__(self, world, title: str, ylabel: str):
        """
        Initializes the Tracker

        Args:
                world (World): The world
                title (str): Graph title
                ylabel (str): y axis label
        """

        Thread.__init__(self)

        self.world = world
        self.title = title
        self.ylabel = ylabel

        self._last_time = time()

        self.x = []
        self.y = []

    def run(self) -> Exception:
        """
        Starts the thread (self)

        Raises:
                NotImplementedError: Should be overwritten in a derived class

        Returns:
                Exception: Will always raise NotImplementedError if called from _Tracker class
        """

        raise NotImplementedError()

    def _timeout(self) -> bool:
        """
        Defines if the timeout between data points has been hit

        Returns:
                bool: True if timeout has been hit, False otherwise
        """

        return time() - self._last_time > TRACKER_TIMEOUT


class RabbitCountTracker(_Tracker):
    """Tracker for Rabbit count"""

    def __init__(self, world):
        """
        Initializes the RabbitCountTracker

        Args:
                world (World): The World
        """

        _Tracker.__init__(self, world, "Rabbit Count", "Rabbits")

    def run(self) -> None:
        """
        Collects the Rabbit count at the runtime
        """

        self.x.append(self.world.runtime / 1000)
        self.y.append(len(self.world.rabbits))
        last_count = len(self.world.rabbits)

        while self.world.running:
            if len(self.world.rabbits) != last_count or self._timeout():
                self._last_time = time()
                last_count = len(self.world.rabbits)

                self.x.append(self.world.runtime / 1000)
                self.y.append(last_count)
            sleep(1)


class FoodCountTracker(_Tracker):
    """Tracker for Food count"""

    def __init__(self, world):
        """
        Initializes the FoodCountTracker

        Args:
                world (World): The world
        """

        _Tracker.__init__(self, world, "Food Count", "Food")

    def run(self) -> None:
        """
        Collects the Food count at the runtime
        """

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


class FoxCountTracker(_Tracker):
    """Tracker for Fox count"""

    def __init__(self, world):
        """
        Initializes the FoxCountTracker

        Args:
                world (World): The world
        """

        _Tracker.__init__(self, world, "Fox Count", "Foxes")

    def run(self) -> None:
        """
        Collects the Fox count at the runtime
        """

        self.x.append(self.world.runtime / 1000)
        self.y.append(len(self.world.foxes))
        last_count = len(self.world.foxes)

        while self.world.running:
            if len(self.world.foxes) != last_count or self._timeout():
                self._last_time = time()
                last_count = len(self.world.foxes)

                self.x.append(self.world.runtime / 1000)
                self.y.append(len(self.world.foxes))
            sleep(1)
