from pirates_vs_cowboys.items import Agent, Crate, Treasure, Bullet


SCREEN_X = 125
SCREEN_Y = 115
OFF_SCREEN_DISTANCE = 125
MAX_BULLETS = 3
AGENT_SPEED = 4  # Needed in both game.py and items.py, should refactor.


class Game:

    def __init__(self, client, game_state, token, game_pyxel):
        self.client = client
        self.players = self.get_players(game_state)
        self.token = token
        self.local_player = self.players[self.token]
        self.pyxel = game_pyxel
        self.bg = [51*i for i in range(0, 5)]
        self.items = [Crate(250 + 75, 125, width=31, height=31),
                      Crate(300 + 75, 125, width=31, height=31)]
                      # Treasure("cowboys", 150, 125, width=10, height=10),
                      # Treasure("pirates", 200, 125, width=10, height=10)]

    def get_players(self, game_state):
        return {token: Agent(**data, width=32, height=32) for token, data in game_state.items()}

    def run(self):
        self.pyxel.run_with_profiler(self.update, self.draw)

    def update(self):
        local_move = self.get_keyboard_move()
        if local_move:
            self.client.send_to.put(local_move)
            instructions = [local_move] + self.client.remote_instructions
        else:
            instructions = self.client.remote_instructions
        for ins in instructions:
            self.execute_instruction(**ins)
        for player in [p for p in self.players.values() if p.active]:
            if player.health <= 0:
                player.active = False
                continue
            player.move()
            if player.won:
                self.player_won(player)
            for item in self.items:
                if not item.active:
                    del item
                    continue
                item.check_and_handle_collision(player)
                item.move()
        self.client.send_local_instructions()

    def get_keyboard_move(self):
        method = None
        kwargs = {}
        if self.pyxel.btnp(self.pyxel.KEY_D):
            method = "player_moved"
            kwargs = {"x": AGENT_SPEED, "facing": 0}
        if self.pyxel.btnp(self.pyxel.KEY_A):
            method = "player_moved"
            kwargs = {"x": -AGENT_SPEED, "facing": 1}
        if self.pyxel.btnp(self.pyxel.KEY_SPACE):
            method = "player_moved"
            kwargs = {"y": -AGENT_SPEED * 4}
        if self.pyxel.btnp(self.pyxel.KEY_Q):
            method = "player_quit"
        if self.pyxel.btnp(self.pyxel.KEY_F):
            if len(self.local_player.bullets) < MAX_BULLETS and not \
               self.local_player.picked_up:
                method = "player_fired"
                kwargs = {"team": self.local_player.team,
                          "x": self.local_player.x + 16,
                          "y": self.local_player.y + 8,
                          "facing": self.local_player.facing}
        if method:
            return {
                "method": method,
                "token": self.token,
                "kwargs": kwargs
            }

    def execute_instruction(self, method=None, token=None,
                            args=None, kwargs=None):
        method = getattr(self, method)
        args = args or []
        kwargs = kwargs or {}
        method(token, *args, **kwargs)

    def player_moved(self, token, **kwargs):
        player = self.players[token]
        player.change_velocity(**kwargs)

    def player_fired(self, _, **kwargs):
        self.items.append(Bullet(**kwargs))

    def player_won(self, player):
        print("{} won!".format(player.team))

    def check_quit(self, move):
        if move["method"] == "player_quit":
            self.player_quit()

    def player_quit(self, *args, **kwargs):
        self.pyxel.quit()

    def draw(self):
        self.pyxel.cls(1)
        self.draw_background()
        self.draw_ship(2)
        self.draw_health()
        for item in self.items + [p for p in self.players.values()]:
            if item.active:
                self.draw_item(item)

    def draw_item(self, item):
        diff = item.x - self.local_player.x
        if abs(diff) < OFF_SCREEN_DISTANCE:
            render_method = getattr(self.pyxel, item.render_method)
            render_method(SCREEN_X + diff, item.y, *item.image_data)

    def draw_background(self):
        for row in range(0, 2):
            diff_x = (self.local_player.x - SCREEN_X) % 255
            left = (diff_x) % 51
            for i in range(0, 6):
                col = (51*i+diff_x) % 255
                if i == 0:
                    self.pyxel.blt(0, 51*row, 1, self.bg[1]-left,
                                   0, 51, 51, 7)
                else:
                    self.pyxel.blt(col, 51*row, 1, self.bg[i % 2],
                                   0, 51, 51, 7)

    def draw_ship(self, row):
        diff_x = (self.local_player.x - SCREEN_X) % 255
        for i in range(0, 6):
            col = (51*i+diff_x) % 255
            if i == 0:
                self.pyxel.blt(0, 51*row, 1, self.bg[3], 0, 51, 51, 7)
            else:
                self.pyxel.blt(col, 51*row, 1, self.bg[3], 0, 51, 51, 7)

    def draw_health(self):
        self.pyxel.rect(10, 10, 10 + self.local_player.health, 20, 8)
        self.pyxel.rectb(10, 10, 60, 20, 0)
        self.pyxel.text(65, 10, "Health", 5)
