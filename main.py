import pyxel

from Agent import Agent
from objects import Crate

from pirates_server.client import Client
from pirates_server.socket_threads import GetFromThread, SendToThread


HOST = "localhost"
# HOST = "piratesvscowboys.com"
PORT = 5000


class App(Client):
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
        pyxel.image(1).load(
            51*0, 0, "assets/background/sky_tiles/skyTile0.png")
        pyxel.image(1).load(
            51*1, 0, "assets/background/sky_tiles/skyTile1.png")
        pyxel.image(1).load(
            51*2, 0, "assets/background/sky_tiles/skyTile2.png")
        pyxel.image(1).load(
            51*3, 0, "assets/background/ship_tiles/test_deck.png")
        self.bg = [51*i for i in range(0, 5)]
        pyxel.image(2).load(0, 0, "assets/background/ship_tiles/Crate0.png")
        game_server_port = self.get_game_server_port()
        socket = self.get_socket(HOST, game_server_port)
        self.player_address = self.get_update(socket)["player_address"]
        self.players = self.wait_for_game(socket)
        self.pos = self.players[self.player_address]
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

    def wait_for_game(self, socket):
        get_update = {"game_started": False}
        while not get_update["game_started"]:
            get_update = self.get_update(socket)
        player_agents = {}
        for player_address, player_data in get_update["players"].items():
            player_agents[player_address] = Agent(player_address,
                                                  **player_data)
        return player_agents

    def drawBackGroung(self, row):
        diff_x = (self.pos.x-self.pos.screen_x) % 255
        left = (diff_x) % 51
        for i in range(0, 6):
            col = (51*i+diff_x) % 255
            if i == 0:
                pyxel.blt(0, 51*row, 1, self.bg[1]-left, 0, 51, 51, 7)
            else:
                pyxel.blt(col, 51*row, 1, self.bg[i % 2], 0, 51, 51, 7)

    def update(self):
        for instruction in self.get_from:
            player_address = instruction.pop("player_address")
            self.execute_remote_instruction(player_address, **instruction)
        for player in self.players.values():
            for testCrate in self.testCrates:
                self.collistion(testCrate, player)
            if player is self.pos:
                continue
            elif not player.has_moved:
                player.move()
                player.has_moved = False
        move = self.pos.get_move()
        self.send_to.put(move)
        self.check_quit(move)


    def player_moved(self, player_address, **kwargs):
        player = self.players[player_address]
        player.move(**kwargs)

    def player_fired(self, player_address, **kwargs):
        player = self.players[player_address]
        player.fire_bullet()

    def player_won(self, player_address, **kwargs):
        winning_player = self.players[player_address]
        winning_team = winning_player.team
        print("{} won!".format(winning_team))

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
        for row in range(0, 2):
            self.drawBackGroung(row)
        for player in self.players.values():
            if player is self.pos:
                # self.draw_player(self.player)
                pass
            else:
                self.draw_player(player)
        self.drawHealth()
        self.drawShipAssets()
        self.drawShip(2)
        pyxel.rectb(self.pos.mesh[0][0], self.pos.mesh[1][0],
                    self.pos.mesh[0][1], self.pos.mesh[1][1], 14)
        for testCrate in self.testCrates:
            pyxel.rectb(testCrate.mesh[0][0], testCrate.mesh[1][0],
                        testCrate.mesh[0][1], testCrate.mesh[1][1], 14)

    def draw_player(self, player):
        print("on screen S:{0} A:{1}".format(player.x, self.pos.x))
        if player.x > self.pos.x - 125 and player.x < self.pos.x + 125:
            diff = player.x - self.pos.x
            if player.x_vel*10 > 1:
                pyxel.blt(self.pos.screen_x + diff, player.screen_y,
                          *self.cowboy1_right, 7)
            elif player.x_vel*10 < -1:
                pyxel.blt(self.pos.screen_x + diff, player.screen_y,
                          *self.cowboy1_left, 7)
            elif player.y_vel*30 > -1:
                pyxel.blt(self.pos.screen_x + diff, player.screen_y,
                          *self.cowboy1_up, 7)
            else:
                pyxel.blt(self.pos.screen_x + diff, player.screen_y,
                          *self.cowboy1_standing, 7)
        bullets = player.getBullets()
        for bullet in bullets:
            pyxel.circ(bullet.inital_x+bullet.x, bullet.inital_y, 1, 0)
            bullet.x += bullet.speed
            if -100 > bullet.x or bullet.x > 100:
                bullets.remove(bullet)
                del bullet

    def collistion(self, obj, agnet):
        LEFT = (obj.mesh[0][1] > agnet.mesh[0][0] and
                obj.mesh[0][0] < agnet.mesh[0][0])
        RIGHT = (obj.mesh[0][1] > agnet.mesh[0][1] and
                 obj.mesh[0][0] < agnet.mesh[0][1])
        ABOVE = obj.mesh[1][0] < agnet.mesh[1][1]
        if RIGHT and ABOVE:
            agnet.collistionAdj(4)
        if LEFT and ABOVE:
            agnet.collistionAdj(3)
        if ABOVE and (RIGHT or LEFT):
            agnet.collistionAdj(2)

        pass

    def drawShipAssets(self):
        for player in self.players.values():
            for testCrate in self.testCrates:
                testCrate.meshMaker(testCrate.x - player.x, testCrate.y)
                if self.pos.x < testCrate.x + 125 and self.pos.x > testCrate.x - 125:
                    pyxel.blt(testCrate.x - self.pos.x, testCrate.y,
                              2, 0, 0, 31, 31, 7)
                pass

    def drawHealth(self):
        pyxel.rect(10, 10, 10 + self.pos.health, 20, 8)
        pyxel.rectb(10, 10, 60, 20, 0)
        pyxel.text(65, 10, "Health", 5)

    def drawShip(self, row):
        diff_x = (self.pos.x-self.pos.screen_x) % 255
        for i in range(0, 6):
            col = (51*i+diff_x) % 255
            if i == 0:
                pyxel.blt(0, 51*row, 1, self.bg[3], 0, 51, 51, 7)
            else:
                pyxel.blt(col, 51*row, 1, self.bg[3], 0, 51, 51, 7)


App()
