import pyxel

from piratesvscowboys.items import Agent, Crate, Treasure, Bullet

from pirates_server.client import Client
from pirates_server.socket_threads import GetFromThread, SendToThread


HOST = "localhost"
# HOST = "piratesvscowboys.com"
PORT = 5000


SCREEN_X = 125
SCREEN_Y = 115
MAX_BULLETS = 3
AGENT_SPEED = 4  # Needed in both main.py and items.py, should refactor.


pyxel.init(250, 153, caption="Pirates vs Cowboys")
pyxel.image(0).load(
    0, 0, "piratesvscowboys/assets/cowboys/cowboy1_standing.png")
pyxel.image(0).load(
    32, 0, "piratesvscowboys/assets/cowboys/cowboy1_left.png")
pyxel.image(0).load(
    64, 0, "piratesvscowboys/assets/cowboys/cowboy1_right.png")
pyxel.image(0).load(
    96, 0, "piratesvscowboys/assets/cowboys/cowboy1_up.png")
pyxel.image(1).load(
    51*0, 0, "piratesvscowboys/assets/background/sky_tiles/skyTile0.png")
pyxel.image(1).load(
    51*1, 0, "piratesvscowboys/assets/background/sky_tiles/skyTile1.png")
pyxel.image(1).load(
    51*2, 0, "piratesvscowboys/assets/background/sky_tiles/skyTile2.png")
pyxel.image(1).load(
    51*3, 0, "piratesvscowboys/assets/background/ship_tiles/test_deck.png")
pyxel.image(2).load(
    0, 0, "piratesvscowboys/assets/background/ship_tiles/Crate0.png")


class App(Client):

    def __init__(self):
        self.bg = [51*i for i in range(0, 5)]
        game_server_port = self.get_game_server_port()
        socket = self.get_socket(HOST, game_server_port)
        self.player_address = self.get_update(socket)["player_address"]
        self.players = self.wait_for_players(socket)
        self.local_player = self.players[self.player_address]
        self.items = [Crate(250 + 75, 125),
                      Crate(300 + 75, 125),
                      Treasure("cowboys", 100, 125),
                      Treasure("pirates", 150, 125)]
        self.get_from = GetFromThread(socket)
        self.send_to = SendToThread(socket)
        self.get_from.start()
        self.send_to.start()
        pyxel.run_with_profiler(self.update, self.draw)

    def get_game_server_port(self):
        assign_socket = self.get_socket(HOST, PORT)
        port = self.get_update(assign_socket)["port"]
        assign_socket.close()
        return port

    def wait_for_players(self, socket):
        get_update = {"game_started": False}
        while not get_update["game_started"]:
            get_update = self.get_update(socket)
        player_agents = {}
        for player_address, player_data in get_update["players"].items():
            player_agents[player_address] = Agent(player_address,
                                                  **player_data)
        return player_agents

    def update(self):
        local_move = self.get_keyboard_move()
        self.send_to.put(local_move)
        instructions = [local_move] + [remote for remote in self.get_from]
        for ins in instructions:
            self.execute_instruction(**ins)
        for player in self.players.values():
            if not player.has_moved:
                player.move()
            if player.won:
                self.player_won(player)
            for item in self.items:
                if not item.active:
                    del item
                    continue
                item.check_collision(player)
                item.move()
            player.has_moved = False

    def get_keyboard_move(self):
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
        if pyxel.btnp(pyxel.KEY_F):
            if len(self.local_player.bullets) < MAX_BULLETS:
                return {
                    "method": "player_fired",
                    "kwargs": {
                        "team": self.local_player.team,
                        "x": self.local_player.x + 16,
                        "y": self.local_player.y + 8,
                        "facing": self.local_player.facing
                    }
                }
        return {
            "method": method,
            "player_address": self.player_address,
            "kwargs": kwargs
        }

    def execute_instruction(self, method=None, player_address=None,
                            args=None, kwargs=None):
        method = getattr(self, method)
        args = args or []
        kwargs = kwargs or {}
        method(player_address, *args, **kwargs)

    def player_moved(self, player_address, **kwargs):
        player = self.players[player_address]
        player.move(**kwargs)

    def player_fired(self, _, **kwargs):
        self.items.append(Bullet(**kwargs))

    def player_won(self, player):
        print("{} won!".format(player.team))

    def check_quit(self, move):
        if move["method"] == "player_quit":
            self.player_quit()

    def player_quit(self, *args, **kwargs):
        self.get_from.stop()
        self.send_to.stop()
        pyxel.quit()

    def do_nothing(self, *args, **kwargs):
        pass

    def draw(self):
        pyxel.cls(1)
        self.draw_background()
        self.draw_ship(2)
        self.draw_health()
        for item in self.items:
            if item.active:
                self.draw_item(item)
        for player in self.players.values():
            self.draw_item(player)

    def draw_item(self, item):
        diff = item.x - self.local_player.x
        if abs(diff) < 125:
            render_method = getattr(pyxel, item.render_method)
            render_method(SCREEN_X + diff, item.y, *item.image_data)

    def draw_background(self):
        for row in range(0, 2):
            diff_x = (self.local_player.x - SCREEN_X) % 255
            left = (diff_x) % 51
            for i in range(0, 6):
                col = (51*i+diff_x) % 255
                if i == 0:
                    pyxel.blt(0, 51*row, 1, self.bg[1]-left, 0, 51, 51, 7)
                else:
                    pyxel.blt(col, 51*row, 1, self.bg[i % 2], 0, 51, 51, 7)

    def draw_ship(self, row):
        diff_x = (self.local_player.x - SCREEN_X) % 255
        for i in range(0, 6):
            col = (51*i+diff_x) % 255
            if i == 0:
                pyxel.blt(0, 51*row, 1, self.bg[3], 0, 51, 51, 7)
            else:
                pyxel.blt(col, 51*row, 1, self.bg[3], 0, 51, 51, 7)

    def draw_health(self):
        pyxel.rect(10, 10, 10 + self.local_player.health, 20, 8)
        pyxel.rectb(10, 10, 60, 20, 0)
        pyxel.text(65, 10, "Health", 5)


App()
