import pyxel


class Rooms:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.borders = [
            [(0+x, 0+y), (51+x, 0+y)],
            [(51+x, 0+y), (51+x, 14+y)],
            [(51+x, 51+y), (0+x, 51+y)],
            [(0+x, 51+y), (0+x, 0+y)]
        ]  # Top,Right,Bottom,Left
