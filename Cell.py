import random


class Cell:
    def __init__(self, location, alive=False):
        self.alive = alive
        self.pressed = False
        self.location = location
        self.grain = 0
        self.graintobe = 0
        self.dualPhased = False
        self.bordertobe = False
        self.to_be = False