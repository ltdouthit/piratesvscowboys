import pyxel
import numpy as np
from PIL import Image


class Sprite:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.x_vel = 0
        self.y_vel = 0

    def move(self):
        if pyxel.btnp(pyxel.KEY_RIGHT):
            #self.x = self.x + 1
            self.x_vel += 1
        elif pyxel.btnp(pyxel.KEY_LEFT):
            #self.x = self.x - 1
            self.x_vel -= 1
        elif pyxel.btnp(pyxel.KEY_UP):
            #self.y = self.y - 1
            self.y_vel -= 1
        elif pyxel.btnp(pyxel.KEY_DOWN):
            #self.y = self.y + 1
            self.y_vel += 1

        self.x += self.x_vel
        self.y += self.y_vel
        self.x_vel = self.x_vel*0.9
        self.y_vel = self.y_vel*0.9


class App:
    pos = Sprite()

    def __init__(self):
        pyxel.init(255, 255, caption="Pirats vs Cowboys")
        pyxel.image(0).load(0, 0, "assets/cowboys/cowboy1_standing.png")
        pyxel.image(0).load(32, 0, "assets/cowboys/cowboy1_left.png")
        pyxel.image(0).load(64, 0, "assets/cowboys/cowboy1_right.png")
        pyxel.image(0).load(96, 0, "assets/cowboys/cowboy1_up.png")
        self.cowboy1_standing = [0, 0, 0, 32, 32]  # Location, Size
        self.cowboy1_left = [0, 32, 0, 32, 32]  # Location, Size
        self.cowboy1_right = [0, 64, 0, 32, 32]  # Location, Size
        self.cowboy1_up = [0, 96, 0, 32, 32]  # Location, Size
        #im_frame = Image.open("assets/background/Background.png")
        #np_frame = np.array(im_frame.getdata())
        # print(im_frame)
        #pyxel.image(1).load(0, 0, "assets/background/Background.png")
        #pyxel.tilemap(0).set(0, 0, ['000102', '202122', 'a0a1a2', 'b0b1b2'])
        #self.background = (1, 0, 0, 255, 255)
        #pyxel.tilemap(0).set(0, 0, "assets/background/Background.png")
        #pyxel.tilemap(0).set(0, 0, ['000102', '202122', 'a0a1a2', 'b0b1b2'])
        #pyxel.tilemap(0).set(0, 0, np_frame)
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        self.pos.move()

    def draw(self):
        pyxel.cls(6)
        if self.pos.x_vel*10 > 1:
            pyxel.blt(self.pos.x, self.pos.y, *self.cowboy1_right, 7)
        elif self.pos.x_vel*10 < -1:
            pyxel.blt(self.pos.x, self.pos.y, *self.cowboy1_left, 7)
        elif self.pos.y_vel*10 < -1:
            pyxel.blt(self.pos.x, self.pos.y, *self.cowboy1_up, 7)
        else:
            pyxel.blt(self.pos.x, self.pos.y, *self.cowboy1_standing, 7)


App()
