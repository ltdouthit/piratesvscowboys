AGENT_SPEED = 4


class Item:

    def __init__(self, x, y, **mesh_offset):
        self.x = x
        self.y = y
        if mesh_offset:
            self.mesh_offset = mesh_offset

    @property
    def mesh(self):
        off1, off2, off3, off4 = self.mesh_offset
        return [(self.x + off1, self.x + off2), (self.y + off3, self.y + off4)]
        # return [(self.x + 5, self.x + 25), (self.y, self.y + 30)]

    def collision(self, agent):
        left = (self.mesh[0][1] > agent.mesh[0][0] and
                self.mesh[0][0] < agent.mesh[0][0])
        right = (self.mesh[0][1] > agent.mesh[0][1] and
                 self.mesh[0][0] < agent.mesh[0][1])
        above = self.mesh[1][0] < agent.mesh[1][1]
        if above and (right or left) or left and above or right and above:
            self.item_collided(agent, left=left, right=right, above=above)

    def item_collided(self, agent, *args, **kwargs):
        pass


class Crate(Item):
    mesh_offset = (5, 25, 0, 30)

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
    mesh_offset = (5, 15, 0, 10)

    def __init__(self, team, *args, **kwargs):
        self.team = team
        super().__init__(*args, **kwargs)

    def item_collided(self, agent, **kwargs):
        if self.team != agent.team:
            agent.picked_up.append(self)
            self.x = agent.x - 5
        elif self.team == agent.team and agent.has_enemy_treasure:
            agent.won = True
