import socket
import _thread

from traffic import HandleTraffic


HOST = ""
PORT = 5000


class PVCS(HandleTraffic):

    def __init__(self, host=HOST, port=PORT):
        self._socket_pool = self._get_socket_pool(host, port)
        self._client_sockets = {}
        self._players = {}
        self._started = False

    def _get_socket_pool(self, host, port):
        socket_pool = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_pool.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_pool.bind((host, port))
        socket_pool.listen(5)
        return socket_pool

    def run(self):
        self.accept_players()
        for player_address, player_socket in self._client_sockets.items():
            _thread.start_new_thread(self.socket_loop,
                                     (player_address, player_socket))
        while True:
            pass  # keep it running, threads handle everything

    def socket_loop(self, player_address, player_socket):
        while True:
            print("SENDING UPDATE: {}".format(player_address))
            send_to = self._players[player_address]["send"]
            self._players[player_address]["send"] = self.send_update(
                player_socket, send_to)
            print("GETTING UPDATE: {}".format(player_address))
            instructions = self.get_update(player_socket)
            self.add_instructions(instructions)

    def accept_players(self):
        next_x, next_y = 0, 0
        while len(self._client_sockets) < 2:
            player_socket, player_address = self._socket_pool.accept()
            player_address = player_address[0] + ":" + str(player_address[1])
            self._client_sockets[player_address] = player_socket
            self._players[player_address] = {"send": [], "x": next_x,
                                             "y": next_y}
            self.send_update(player_socket, {"player_address": player_address})
            next_x += 50
        for player_address, player_socket in self._client_sockets.items():
            self.send_update(
                player_socket, {"game_started": True, "players": self._players}
            )

    def add_instructions(self, instructions):
        for player_address in self._players:
            for ins in instructions:
                if ins is None:
                    ins = {"method": "do_nothing", "player_address": None}
                self._players[player_address]["send"].append(ins)

    def check_to_start(self):
        self._started = True

    def quit(self, *args, **kwargs):
        self._started = False
