import pyxel

MAX_BULLETS = 3
BULLET_SPEED = 2
ARENA_SIZE = [0, 1000]
AGENT_SPEED = 4


class Agent:

    def __init__(self):
        self.x = 125
        self.y = 50
        self.x_vel = 0
        self.y_vel = 0
        self.screen_x = 125
        self.screen_y = 115
        self.facing = 0
        self.bullets = []

    def move(self):
        if pyxel.btnp(pyxel.KEY_D):
            #self.x = self.x + 1
            self.facing = 0
            self.x_vel += AGENT_SPEED
        elif pyxel.btnp(pyxel.KEY_A):
            #self.x = self.x - 1
            self.facing = 1
            self.x_vel -= AGENT_SPEED
        elif pyxel.btnp(pyxel.KEY_SPACE):
            #self.y = self.y - 1
            self.y_vel -= 10
        elif pyxel.btnp(pyxel.KEY_F):
            if len(self.bullets) < MAX_BULLETS:
                self.bullets.append(Bullet(self.screen_x+16, self.screen_y+8, self.facing))

        if self.x < ARENA_SIZE[0]:
            self.x_vel += 10
        if self.x > ARENA_SIZE[1]:
            self.x_vel -= 10
        self.x += self.x_vel
        if self.screen_y > 120:
            self.y_vel += -1
        if self.screen_y < -10:
            self.screen_y = -0
            self.y_vel = 0
        self.screen_y += self.y_vel + 3
        self.x_vel = self.x_vel*0.9
        self.y_vel = self.y_vel*0.9
        print("x:{0} \n y:{1}".format(self.x, self.screen_y))

    def getBullets(self):
        return self.bullets


class Bullet:
    def __init__(self, x, y, dir):
        self.x = x
        self.y = y
        if dir == 0:
            self.speed = BULLET_SPEED
        else:
            self.speed = -BULLET_SPEED

    def setPos(self, x, y):
        self.x = x
        self.y = y
