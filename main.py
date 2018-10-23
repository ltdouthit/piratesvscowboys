import pyxel
from Agent import Agent


class App:
    pos = Agent()

    def __init__(self):
        pyxel.init(250, 153, caption="Pirats vs Cowboys")
        pyxel.image(0).load(0, 0, "assets/cowboys/cowboy1_standing.png")
        pyxel.image(0).load(32, 0, "assets/cowboys/cowboy1_left.png")
        pyxel.image(0).load(64, 0, "assets/cowboys/cowboy1_right.png")
        pyxel.image(0).load(96, 0, "assets/cowboys/cowboy1_up.png")
        self.cowboy1_standing = [0, 0, 0, 32, 32]  # Location, Size
        self.cowboy1_left = [0, 32, 0, 32, 32]  # Location, Size
        self.cowboy1_right = [0, 64, 0, 32, 32]  # Location, Size
        self.cowboy1_up = [0, 96, 0, 32, 32]  # Location, Size
        pyxel.image(1).load(51*0, 0, "assets/background/Background1/test_bg0.png")
        pyxel.image(1).load(51*1, 0, "assets/background/Background1/test_bg1.png")
        pyxel.image(1).load(51*2, 0, "assets/background/Background1/test_bg2.png")
        pyxel.image(1).load(51*3, 0, "assets/background/Background1/test_bg3.png")
        pyxel.image(1).load(51*4, 0, "assets/background/Background1/test_bg4.png")
        self.bg = [51*i for i in range(0, 5)]
        self.deck = [1, 125, 0, 125, 100]
        pyxel.run(self.update, self.draw)

    def drawBackGroung(self, row):
        diff_x = (self.pos.x-self.pos.screen_x) % 255
        diff_y = (self.pos.y-self.pos.screen_y) % 255
        left = (diff_x) % 51
        for i in range(0, 6):
            col = (51*i+diff_x) % 255
            if i == 0:
                pyxel.blt(0, 51*row, 1, self.bg[1]-left, 0, 51, 51, 7)
            else:
                pyxel.blt(col, 51*row, 1, self.bg[i % 3], 0, 51, 51, 7)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        self.pos.move()

    def draw(self):
        pyxel.cls(4)
        for row in range(0, 3):
            self.drawBackGroung(row)
        if self.pos.x_vel*10 > 1:
            pyxel.blt(self.pos.screen_x, self.pos.screen_y, *self.cowboy1_right, 7)
        elif self.pos.x_vel*10 < -1:
            pyxel.blt(self.pos.screen_x, self.pos.screen_y, *self.cowboy1_left, 7)
        elif self.pos.y_vel*30 > -1:
            pyxel.blt(self.pos.screen_x, self.pos.screen_y, *self.cowboy1_up, 7)
        else:
            pyxel.blt(self.pos.screen_x, self.pos.screen_y, *self.cowboy1_standing, 7)
        pyxel.rect(200, 0, 250, 150, 12)
        bullets = self.pos.getBullets()
        for bullet in bullets:
            pyxel.pix(bullet.x, bullet.y, 12)
            bullet.x += bullet.speed
            if 0 > bullet.x or bullet.x > 255:
                bullets.remove(bullet)
                del bullet


App()
