import pyxel

MAX_BULLETS = 3
BULLET_SPEED = 2
ARENA_SIZE = [0, 1000]
AGENT_SPEED = 4


class Agent:

    def __init__(self, x, y, player_address):
        self.x = x
        self.y = y
        self.player_address = player_address
        self.x_vel = 0
        self.y_vel = 0
        self.screen_x = 125
        self.screen_y = 115
        self.facing = 0
        self.bullets = []
        self.health = 30  # 50 Max Health
        self.mesh = self.meshMaker(self.x, self.screen_y)
        self.had_movment = False;


    def get_move(self):
        method = "do_nothing"
        kwargs = {}
        if pyxel.btnp(pyxel.KEY_D):
            method = "player_moved"
            kwargs = {"facing": 0, "x_vel": AGENT_SPEED}
        if pyxel.btnp(pyxel.KEY_A):
            method = "player_moved"
            kwargs = {"facing": 1, "x_vel": -AGENT_SPEED}
        if pyxel.btnp(pyxel.KEY_SPACE):
            method = "player_moved"
            kwargs = {"y_vel": -10}
        if pyxel.btnp(pyxel.KEY_Q):
            method = "player_quit"
        self.move(**kwargs)
        if pyxel.btnp(pyxel.KEY_F):
            self.fire_bullet()
            if len(self.bullets) < MAX_BULLETS:
                method = "player_fired"
        return {
            "method": method,
            "player_address": self.player_address,
            "kwargs": kwargs
        }


    def move(self, x_vel=None, y_vel=None, facing=None):
        self.had_movment = True
        if x_vel is not None:
            self.x_vel += x_vel
        if y_vel is not None:
            self.y_vel += y_vel
        if facing is not None:
            self.facing = facing
        if self.x < ARENA_SIZE[0]:
            self.x_vel += AGENT_SPEED
        if self.x > ARENA_SIZE[1]:
            self.x_vel -= AGENT_SPEED
        if self.screen_y > 120:
            self.y_vel += -1
        if self.screen_y < -10:
            self.screen_y = 0
            self.y_vel = 0
        self.x += self.x_vel
        self.screen_y += self.y_vel + 3
        self.x_vel = 0#self.x_vel*0.9
        self.y_vel = self.y_vel*0.9
        self.mesh = self.meshMaker(self.screen_x, self.screen_y)

    def fire_bullet(self):
        self.bullets.append(Bullet(self.screen_x+16, self.screen_y+8,
                                   self.facing))

    def getBullets(self):
        return self.bullets

    def meshMaker(self, x, y):
        return [(x+7, x+24), (y, y+31)]

    def collistionAdj(self, dir):
        # 1=Up, 2=Down, 3=Left, 4=Right
        if dir == 2:
            self.y_vel -= AGENT_SPEED
            self.x_vel = self.x_vel*0.05
        elif dir == 3:
            self.x_vel += AGENT_SPEED
            self.y_vel = 0
        elif dir == 4:
            self.x_vel -= AGENT_SPEED
            self.y_vel = 0


class Bullet:
    def __init__(self, x, y, dir):
        self.inital_x = x
        self.inital_y = y
        self.x = 0
        self.y = 0
        if dir == 0:
            self.speed = BULLET_SPEED
        else:
            self.speed = -BULLET_SPEED

    def setPos(self, x, y):
        self.x = x
        self.y = y
