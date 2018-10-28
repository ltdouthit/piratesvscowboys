import threading
import socket

from .traffic import SendTraffic
from .socket_threads import GetFromThread, SendToThread


HOST = ""
PORT = 5000


class Server(SendTraffic):

    def __init__(self, host=HOST, port=PORT, listen=5):
        self.socket_pool = self.get_socket_pool(host, port, listen)
        self.host = host or "localhost"
        self.port = port
        self.listen = listen
        self.running = True

    def get_socket_pool(self, host, port, listen):
        socket_pool = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_pool.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_pool.bind((host, port))
        socket_pool.listen(listen)
        return socket_pool

    def __repr__(self):
        print("{}({}, port={}, listen={})".format(
            self.__class__.__name__, self.host, self.port, self.listen)
        )


class MatchMaker(Server):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("Launching matchmaker on port {}.".format(PORT))
        self.port = PORT + 1
        self.game_threads = {}

    def run(self):
        while True:
            player_socket, _ = self.socket_pool.accept()
            game_thread = self.game_threads.get(self.port)
            if game_thread and game_thread.game.started:
                print("Game started on port {}.".format(self.port))
                self.port += 1
                game_thread = None
            if not game_thread:
                print("Game thread started for port {}.".format(self.port))
                game_thread = GameThread(self.port)
                game_thread.start()
                self.game_threads[self.port] = game_thread
            self.send_update(player_socket, {"port": self.port})
            player_socket.close()


class GameThread(threading.Thread):

    def __init__(self, port):
        super().__init__()
        self.game = Game(HOST, port)
        self.running = True

    def run(self):
        self.game.run()
        while self.game.running:
            pass
        self.stop()

    def stop(self):
        self.running = False
        self.join()


class Game(Server):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.players = {}
        self.started = False

    def run(self):
        self.accept_players()
        while self.running:
            for player in self.players.values():
                update = player["get_from"].get()
                if not update:
                    continue
                elif update["method"] == "player_quit":
                    self.running = False
                for other in self.players.values():
                    if player == other:
                        continue
                    other["send_to"].put(update)

    def accept_players(self):
        next_x, next_y, next_team = 0, 0, 0
        while len(self.players) < 2:
            player_socket, player_address = self.socket_pool.accept()
            player_address = player_address[0] + ":" + str(player_address[1])
            if not next_team % 2:
                team = "cowboys"
            else:
                team = "pirates"
            self.players[player_address] = {
                "get_from": GetFromThread(player_socket),
                "send_to": SendToThread(player_socket),
                "json_data": {"x": next_x, "y": next_y, "team": team}
            }
            self.send_update(player_socket, {"player_address": player_address})
            next_x += 50
            next_team += 1
        player_json = {player_address: player["json_data"]
                       for player_address, player in self.players.items()}
        for player in self.players.values():
            player["send_to"].send_update(
                {"game_started": True, "players": player_json}
            )
            player["send_to"].start()
            player["get_from"].start()
        self.started = True
