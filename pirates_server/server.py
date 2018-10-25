import socket
import threading
import queue

from traffic import HandleTraffic


HOST = ""
PORT = 5000


class ClientSocketThread(HandleTraffic, threading.Thread):

    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        self.send_to = queue.Queue()
        self.get_from = queue.Queue()

    def run(self):
        while True:
            try:
                send = self.send_to.get(block=False)
            except queue.Empty:
                send = None
            self.send_update(self.socket, send)
            updates = self.get_update(self.socket)
            self.get_from.put(updates)


class PVCS(HandleTraffic):

    def __init__(self, host=HOST, port=PORT):
        self._socket_pool = self._get_socket_pool(host, port)
        self.players = {}

    def _get_socket_pool(self, host, port):
        socket_pool = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_pool.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_pool.bind((host, port))
        socket_pool.listen(5)
        return socket_pool

    def run(self):
        self.accept_players()
        while True:
            for player in self.players.values():
                queue_empty = False
                while not queue_empty:
                    try:
                        update = player["thread"].get_from.get(block=False)
                        for other in self.players.values():
                            if other != player:
                                other["thread"].send_to.put(update)
                    except queue.Empty:
                        queue_empty = True

    def accept_players(self):
        next_x, next_y = 0, 0
        while len(self.players) < 2:
            player_socket, player_address = self._socket_pool.accept()
            player_address = player_address[0] + ":" + str(player_address[1])
            socket_thread = ClientSocketThread(player_socket)
            self.players[player_address] = {
                "thread": socket_thread,
                "x": next_x,
                "y": next_y
            }
            self.send_update(player_socket, {"player_address": player_address})
            next_x += 50
        player_json = {player_address: {"x": player["x"], "y": player["y"]}
                       for player_address, player in self.players.items()}
        for player in self.players.values():
            socket = player["thread"].socket
            self.send_update(socket,
                             {"game_started": True, "players": player_json})
            player["thread"].start()
