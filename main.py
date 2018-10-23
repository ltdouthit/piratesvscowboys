import pyxel
from agent import Agent
from objects import Crate


class App:
    pos = Agent()
    testCrates = [Crate(250 + 75, 125), Crate(300 + 75, 125)]

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
        pyxel.image(1).load(51*0, 0, "assets/background/sky_tiles/skyTile0.png")
        pyxel.image(1).load(51*1, 0, "assets/background/sky_tiles/skyTile1.png")
        pyxel.image(1).load(51*2, 0, "assets/background/sky_tiles/skyTile2.png")
        pyxel.image(1).load(51*3, 0, "assets/background/ship_tiles/test_deck.png")
        self.bg = [51*i for i in range(0, 5)]
        pyxel.image(2).load(0, 0, "assets/background/ship_tiles/Crate0.png")
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
                pyxel.blt(col, 51*row, 1, self.bg[i % 2], 0, 51, 51, 7)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        self.pos.move()
        for testCrate in self.testCrates:
            self.collistion(testCrate, self.pos)

    def draw(self):
        pyxel.cls(1)
        for row in range(0, 2):
            self.drawBackGroung(row)
        if self.pos.x_vel*10 > 1:
            pyxel.blt(self.pos.screen_x, self.pos.screen_y, *self.cowboy1_right, 7)
        elif self.pos.x_vel*10 < -1:
            pyxel.blt(self.pos.screen_x, self.pos.screen_y, *self.cowboy1_left, 7)
        elif self.pos.y_vel*30 > -1:
            pyxel.blt(self.pos.screen_x, self.pos.screen_y, *self.cowboy1_up, 7)
        else:
            pyxel.blt(self.pos.screen_x, self.pos.screen_y, *self.cowboy1_standing, 7)
        bullets = self.pos.getBullets()
        for bullet in bullets:
            pyxel.circ(bullet.inital_x+bullet.x, bullet.inital_y, 1, 0)
            bullet.x += bullet.speed
            if -100 > bullet.x or bullet.x > 100:
                bullets.remove(bullet)
                del bullet
        self.drawHealth()
        self.drawShipAssets()
        self.drawShip(2)
        pyxel.rectb(self.pos.mesh[0][0], self.pos.mesh[1][0],
                    self.pos.mesh[0][1], self.pos.mesh[1][1], 14)
        for testCrate in self.testCrates:
            pyxel.rectb(testCrate.mesh[0][0], testCrate.mesh[1][0],
                        testCrate.mesh[0][1], testCrate.mesh[1][1], 14)

    def collistion(self, obj, agnet):
        LEFT = obj.mesh[0][1] > agnet.mesh[0][0] and obj.mesh[0][0] < agnet.mesh[0][0]
        RIGHT = obj.mesh[0][1] > agnet.mesh[0][1] and obj.mesh[0][0] < agnet.mesh[0][1]
        ABOVE = obj.mesh[1][0] < agnet.mesh[1][1]
        if RIGHT and ABOVE:
            agnet.collistionAdj(4)
        if LEFT and ABOVE:
            agnet.collistionAdj(3)
        if ABOVE and (RIGHT or LEFT):
            agnet.collistionAdj(2)

        pass

    def drawShipAssets(self):
        for testCrate in self.testCrates:
            testCrate.meshMaker(testCrate.x - self.pos.x, testCrate.y)
            if self.pos.x < testCrate.x + 125:
                pyxel.blt(testCrate.x - self.pos.x, testCrate.y, 2, 0, 0, 31, 31, 7)
            pass

    def drawHealth(self):
        pyxel.rect(10, 10, 10 + self.pos.health, 20, 8)
        pyxel.rectb(10, 10, 60, 20, 0)
        pyxel.text(65, 10, "Health", 5)

    def drawShip(self, row):
        diff_x = (self.pos.x-self.pos.screen_x) % 255
        diff_y = (self.pos.y-self.pos.screen_y) % 255
        left = (diff_x) % 51
        for i in range(0, 6):
            col = (51*i+diff_x) % 255
            if i == 0:
                pyxel.blt(0, 51*row, 1, self.bg[3], 0, 51, 51, 7)
            else:
                pyxel.blt(col, 51*row, 1, self.bg[3], 0, 51, 51, 7)


App()
