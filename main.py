import pyxel
import time


class Sprite:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.x_vel = 0
        self.y_vel = 0

    def move(self):
        if pyxel.btnp(pyxel.KEY_RIGHT):
            #            self.x = self.x + 1
            self.x_vel += 1
        if pyxel.btnp(pyxel.KEY_LEFT):
            #self.x = self.x - 1
            self.x_vel -= 1
        if pyxel.btnp(pyxel.KEY_UP):
            #self.y = self.y - 1
            self.y_vel -= 1
        if pyxel.btnp(pyxel.KEY_DOWN):
            #self.y = self.y + 1
            self.y_vel += 1

        self.x += self.x_vel
        self.y += self.y_vel
        self.x_vel = self.x_vel*0.9
        self.y_vel = self.y_vel*0.9


class App:
    pos = Sprite()

    def __init__(self):
        pyxel.init(255, 255, caption="Hello Pyxel")
        pyxel.image(0).load(0, 0, "assets/sprite/sprite_0.png")
        pyxel.image(0).load(32, 0, "assets/sprite/sprite_1.png")
        self.sprite_0 = [0, 0, 0, 32, 32]  # Location, Size
        self.sprite_1 = [0, 32, 0, 32, 32]  # Location, Size

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        self.pos.move()

    def draw(self):
        pyxel.cls(6)
        #pyxel.pix(self.pos.x, self.pos.y, 8)
        if self.pos.x_vel*10 > 0:
            pyxel.blt(self.pos.x, self.pos.y, *self.sprite_0, 7)
        elif self.pos.x_vel*10 < 0:
            pyxel.blt(self.pos.x, self.pos.y, *self.sprite_1, 7)
        pyxel.text(55, 41, "{0}".format(self.pos.x_vel), pyxel.frame_count % 16)
        #pyxel.blt(61, 66, *self.sprite_0, 0)


App()
