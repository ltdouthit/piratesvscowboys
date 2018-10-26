import threading
import socket

from traffic import HandleTraffic, GetFromThread, SendToThread


HOST = ""
PORT = 5000


class Server(HandleTraffic):

    def __init__(self, host=HOST, port=PORT, listen=5):
        self.socket_pool = self.get_socket_pool(host, port, listen)
        self.running = True

    def get_socket_pool(self, host, port, listen):
        socket_pool = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_pool.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_pool.bind((host, port))
        socket_pool.listen(listen)
        return socket_pool


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
        self.game = PVCS(HOST, port)

    def run(self):
        self.game.run()
        while self.game.running:
            pass


class PVCS(Server):

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
                for other in self.players.values():
                    if player == other:
                        continue
                    other["send_to"].put(update)

    def accept_players(self):
        next_x, next_y = 0, 0
        while len(self.players) < 2:
            player_socket, player_address = self.socket_pool.accept()
            player_address = player_address[0] + ":" + str(player_address[1])
            self.players[player_address] = {
                "get_from": GetFromThread(player_socket),
                "send_to": SendToThread(player_socket),
                "x": next_x,
                "y": next_y
            }
            self.send_update(player_socket, {"player_address": player_address})
            next_x += 50
        player_json = {player_address: {"x": player["x"], "y": player["y"]}
                       for player_address, player in self.players.items()}
        for player in self.players.values():
            player["send_to"].send_update(
                {"game_started": True, "players": player_json}
            )
            player["send_to"].start()
            player["get_from"].start()
        self.started = True
