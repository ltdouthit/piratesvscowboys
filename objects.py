import pyxel


class Crate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.mesh = [(self.x+8, self.x-8), (self.y+8, self.y-8)]

    def meshMaker(self, x, y):
        self.mesh = [(x+5, x+25), (y, y+30)]
