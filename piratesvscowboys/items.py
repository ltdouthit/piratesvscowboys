AGENT_SPEED = 4
TREASURE_FALL_SPEED = 5
BULLET_SPEED = 2
ARENA_SIZE = [0, 1000]

SCREEN_X = 125
SCREEN_Y = 115


class Item:
    render_method = "blt"  # pyxel method to call to render this item.
    image_data = ()  # Data to pass to render method. X and Y will be supplied.
    mesh_offset = []  # [(x_offset, x_offset2, y_offset, y_offset2)]

    def __init__(self, x, y, image_data=None, active=True, **mesh_offset):
        self.x = x
        self.y = y
        self.active = active
        self.has_moved = False

    @property
    def mesh(self):
        off1, off2, off3, off4 = self.mesh_offset
        return [(self.x + off1, self.x + off2), (self.y + off3, self.y + off4)]

    def check_collision(self, agent):
        left = (self.mesh[0][1] > agent.mesh[0][0] and
                self.mesh[0][0] < agent.mesh[0][0])
        right = (self.mesh[0][1] > agent.mesh[0][1] and
                 self.mesh[0][0] < agent.mesh[0][1])
        above = self.mesh[1][0] < agent.mesh[1][1]
        if above and (right or left) or left and above or right and above:
            self.item_collided(agent, left=left, right=right, above=above)

    def item_collided(self, agent, *args, **kwargs):
        """Override in child classes where applicable."""
        pass

    def move(self, *args, **kwargs):
        """Override in child classes where applicable."""
        self.has_moved = True


class Crate(Item):
    mesh_offset = (5, 25, 0, 30)
    image_data = (2, 0, 0, 31, 31, 7)

    def item_collided(self, agent, above=False, right=False,
                      below=False, left=False):
        if above and (right or left):
            agent.y_vel -= AGENT_SPEED
            agent.x_vel = 0
        elif left and above:
            agent.x_vel += AGENT_SPEED
            agent.y_vel = 0
        elif right and above:
            agent.x_vel -= AGENT_SPEED
            agent.y_vel = 0


class Treasure(Item):

    def __init__(self, team, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.team = team
        self.image_data = (2, 0, 0, 31, 31, 7)  # TEMP: Borrowing crate image.
        self.mesh_offset = (5, 15, 0, 10)
        self.held_by = None

    def check_collision(self, *args, **kwargs):
        if not self.held_by:
            super().check_collision(*args, **kwargs)

    def item_collided(self, agent, **kwargs):
        if self.team != agent.team:
            agent.picked_up.append(self)
            self.held_by = agent
            self.x = agent.x - 5
        elif self.team == agent.team and agent.has_enemy_treasure:
            agent.won = True

    def move(self):
        if self.held_by:
            self.x = self.held_by.x - 5
            self.y = self.held_by.y


team_images = {
    "cowboys": dict(standing=[0, 0, 0, 32, 32, 7], left=[0, 32, 0, 32, 32, 7],
                    right=[0, 64, 0, 32, 32, 7], up=[0, 96, 0, 32, 32, 7]),
    "pirates": dict(standing=[0, 0, 0, 32, 32, 7], left=[0, 32, 0, 32, 32, 7],
                    right=[0, 64, 0, 32, 32, 7], up=[0, 96, 0, 32, 32, 7])
}


class Agent(Item):

    def __init__(self, player_address, team, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player_address = player_address
        self.team = team
        self.image_dict = team_images[team]
        self.bullets = []
        self.picked_up = []
        self.health = 30
        self.x_vel = 0
        self.y_vel = 0
        self.has_moved = False
        self.facing = 1
        self.won = False
        self.mesh_offset = (7, 24, 0, 31)

    @property
    def image_data(self):
        if self.x_vel * 10 > 1:
            return self.image_dict["right"]
        elif self.x_vel * 10 < 1:
            return self.image_dict["left"]
        elif self.y_vel * 30 > -1:
            return self.image_dict["up"]
        else:
            return self.image_dict["standing"]

    def move(self, x_vel=None, y_vel=None, facing=None):
        self.has_moved = True
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
        if self.y > 120:
            self.y_vel += -1
        if self.y < -10:
            self.y_vel = 0
        self.x += self.x_vel
        self.y += self.y_vel + 3
        self.x_vel = self.x_vel * 0.9
        self.y_vel = self.y_vel * 0.9

    @property
    def has_enemy_treasure(self):
        return [i for i in self.picked_up
                if isinstance(i, Treasure) and i.team != self.team]


class Bullet(Item):

    def __init__(self, facing, team, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if facing == 0:
            self.speed = BULLET_SPEED
        else:
            self.speed = -BULLET_SPEED
        self.last_x = self.x
        self.team = team
        self.mesh_offset = (5, 5, 5, 5)
        self.render_method = "circ"
        self.image_data = (1, 0)

    def move(self):
        self.last_x = self.x
        self.x += self.speed
        if abs(self.x) > 100:
            self.active = False
        self.has_moved = True

    def check_collision(self, agent):
        if agent.team == self.team:
            return
        bullet_diff = abs(self.x - self.last_x)
        player_diff = abs(agent.x - self.x)
        if abs(player_diff - bullet_diff) < 5 and abs(agent.y - self.y) < 15:
            self.item_collided(agent)

    def item_collided(self, agent, **kwargs):
        agent.health -= 10
        self.active = False
