class Crate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def mesh(self):
        return [(self.x + 5, self.x + 25), (self.y, self.y + 30)]

    def collision(self, agent):
        left = (self.mesh[0][1] > agent.mesh[0][0] and
                self.mesh[0][0] < agent.mesh[0][0])
        right = (self.mesh[0][1] > agent.mesh[0][1] and
                 self.mesh[0][0] < agent.mesh[0][1])
        above = self.mesh[1][0] < agent.mesh[1][1]
        agent.collision_adjust(right=right, above=above, left=left)
