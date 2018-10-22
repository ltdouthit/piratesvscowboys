import pyxel
from Agent import Agent
from Rooms import Rooms


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
        pyxel.image(1).load(51*0, 0, "assets/background/background/background0.png")
        pyxel.image(1).load(51*1, 0, "assets/background/background/background1.png")
        pyxel.image(1).load(51*2, 0, "assets/background/background/background2.png")
        self.bg = [51*i for i in range(0, 3)]
        pyxel.image(1).load(0, 51, "assets/background/room1.png")
        self.rooms = self.makeRooms()
        pyxel.run(self.update, self.draw)

    def makeRooms(self):
        loc = [0, 400]
        return [Rooms(loc[i], 102) for i in range(0, 2)]

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
        '''
        Find Collisions
        '''
        for box in self.pos.screen_x

    def draw(self):
        pyxel.cls(4)
        for row in range(0, 2):
            self.drawBackGroung(row)
        self.drawRooms()

        if self.pos.x_vel*10 > 1:
            pyxel.blt(self.pos.x, self.pos.screen_y, *self.cowboy1_right, 7)
        elif self.pos.x_vel*10 < -1:
            pyxel.blt(self.pos.x, self.pos.screen_y, *self.cowboy1_left, 7)
        elif self.pos.y_vel*30 > -1:
            pyxel.blt(self.pos.x, self.pos.screen_y, *self.cowboy1_up, 7)
        else:
            pyxel.blt(self.pos.x, self.pos.screen_y, *self.cowboy1_standing, 7)

        self.drawBullets()

    def drawRooms(self):
        diff_x = (self.pos.x-self.pos.screen_x)
        diff_y = (self.pos.y-self.pos.screen_y)
        left = (diff_x) % 51
        for room in self.rooms:
            if (self.pos.screen_x - 125 < room.x):
                pyxel.blt(room.x+diff_x, room.y, 1, 0, 51, 51, 51, 7)
            if (self.pos.screen_x + 125 > room.x):
                pyxel.blt(room.x+diff_x, room.y, 1, 0, 51, 51, 51, 7)

    def drawBullets(self):
        bullets = self.pos.getBullets()
        for bullet in bullets:
            pyxel.pix(bullet.x, bullet.y, 12)
            bullet.x += bullet.speed
            if 0 > bullet.x or bullet.x > 255:
                bullets.remove(bullet)
                del bullet


App()
