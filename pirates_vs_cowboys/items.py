AGENT_SPEED = 4
TREASURE_FALL_SPEED = 5
BULLET_SPEED = 2

MIN_X = 0
MAX_X = 1000
MAX_Y = 120
MIN_Y = -10

VELOCITY_DECAY = 0.9

SCREEN_X = 125


class BaseItem:
    image_data = ()  # Data to pass to render method. X and Y will be supplied.
    render_method = "blt"

    def __init__(self, x=None, y=None, width=1, height=1, x_vel=0, y_vel=0, active=True, **attributes):
        self.x = x
        self.y = y
        self.width = int(width / 2) or 1
        self.height = int(height / 2) or 1
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.active = active
        for attribute, value in attributes.items():
            setattr(self, attribute, value)

    def check_and_handle_collision(self, obj):
        if (self.x <= obj.x + obj.width) and (self.x + self.width >= obj.x) \
           and (self.y <= obj.y + obj.height) and (self.y + self.height >= obj.y):
            above = self.y > obj.y
            right = self.x < obj.x
            below = self.y < obj.y
            left = self.x > obj.x
            return self.handle_collision(obj, above=above, right=right,
                                         below=below, left=left)

    def handle_collision(self, obj, *args, **kwargs):
        """Override in child classes where applicable."""
        pass

    def move(self, *args, **kwargs):
        """Override in child classes where applicable."""
        pass


class Crate(BaseItem):
    image_data = (2, 0, 0, 31, 31, 7)

    def handle_collision(self, obj, above, right, below, left):
        if above:
            obj.y_vel -= int(obj.speed / 2) or 1
        elif right:
            obj.x_vel += int(obj.speed / 2) or 1
        elif below:
            obj.y_vel += int(obj.speed / 2) or 1
        elif left:
            obj.x_vel -= int(obj.speed / 2) or 1


class Treasure(BaseItem):

    def __init__(self, team, *args, **kwargs):
        self.team = team
        self.image_data = (2, 0, 0, 31, 31, 7)  # TEMP: Borrowing crate image.
        self.held_by = None
        super().__init__(*args, **kwargs)

    def check_and_handle_collision(self, obj, *args, **kwargs):
        if not self.held_by and not getattr(obj, "picked_up"):
            super().check_and_handle_collision(obj, *args, **kwargs)

    def handle_collision(self, agent, *args, **kwargs):
        if agent.team == self.team and agent.has_enemy_treasure:
            agent.won = True
        else:
            agent.picked_up.append(self)
            self.held_by = agent

    def move(self):
        if self.held_by:
            self.x = self.held_by.x - 5
            self.y = self.held_by.y


agent_team_images = {
    "cowboys": dict(standing=[0, 0, 0, 32, 32, 7], left=[0, 32, 0, 32, 32, 7],
                    right=[0, 64, 0, 32, 32, 7], up=[0, 96, 0, 32, 32, 7]),
    "pirates": dict(standing=[0, 0, 0, 32, 32, 7], left=[0, 32, 0, 32, 32, 7],
                    right=[0, 64, 0, 32, 32, 7], up=[0, 96, 0, 32, 32, 7])
}


class Agent(BaseItem):

    def __init__(self, team, health=30, width=10, height=10, *args, **kwargs):
        super().__init__(width=width, height=height, *args, **kwargs)
        self.team = team
        self.health = health
        self.image_dict = agent_team_images[team]
        self.bullets = []
        self.picked_up = []
        self.facing = 1
        self.won = False
        self.speed = AGENT_SPEED

    @property
    def image_data(self):
        if self.x_vel * 10 > 1:
            return self.image_dict["right"]
        elif self.x_vel * 10 < 1:
            return self.image_dict["left"]
#        elif self.y_vel * 30 > -1:
#            return self.image_dict["up"]
#        else:
#            return self.image_dict["standing"]

    def change_velocity(self, x=None, y=None, facing=None):
        if x:
            self.x_vel += x
        if y:
            self.y_vel += y
        if facing is not None:
            self.facing = facing

    def move(self):
        if self.x < MIN_X:
            self.x_vel += AGENT_SPEED
        if self.x > MAX_X:
            self.x_vel -= AGENT_SPEED
        if self.y < MAX_Y and self.y > MIN_Y:
            self.y_vel += int(AGENT_SPEED / 2)
        elif self.y > MAX_Y:
            self.y = MAX_Y
            self.y_vel = 0
        elif self.y < MIN_Y:
            self.y_vel = AGENT_SPEED
        self.x += self.x_vel
        self.y += self.y_vel
        self.x_vel *= VELOCITY_DECAY
        self.y_vel *= VELOCITY_DECAY

    @property
    def has_enemy_treasure(self):
        for item in self.picked_up:
            if isinstance(item, Treasure) and item.team != self.team:
                return True


class Bullet(BaseItem):
    render_method = "circ"
    image_data = (1, 0)

    def __init__(self, team, facing, damage=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.team = team
        self.facing = facing
        self.damage = damage
        super().__init__(*args, **kwargs)

    def move(self):
        if self.facing == 0:
            self.x += BULLET_SPEED
        elif self.facing == 1:
            self.x -= BULLET_SPEED

    def check_and_handle_collision(self, obj, *args, **kwargs):
        if obj.team != self.team:
            super().check_and_handle_collision(obj, *args, **kwargs)

    def handle_collision(self, obj, *args, **kwargs):
        obj.health -= self.damage
        self.active = False
