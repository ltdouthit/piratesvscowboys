import socket

from pirates_server import HandleTraffic


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
        while True:
            print("LOOP START")
            for player_address, player_socket in self._client_sockets.items():
                print("GETTING UPDATE: {}".format(player_address))
                instruction = self.get_update(player_socket)
                if instruction:
                    self.execute(player_address, **instruction)
                print("SENDING UPDATE: {}".format(player_address))
                send_to = self._players[player_address]["send"]
                self._players[player_address]["send"] = self.send_update(
                    player_socket, send_to)

    def accept_players(self):
        while len(self._client_sockets) < 2:
            player_socket, player_address = self._socket_pool.accept()
            self._client_sockets[player_address] = player_socket
            self._players[player_address] = {"send": []}

    def check_to_start(self):
        self._started = True

    def execute(self, player_address, method, args=None, kwargs=None):
        method = getattr(self, method)
        args = args or []
        kwargs = kwargs or {}
        method(player_address, *args, **kwargs)

    def quit(self, *args, **kwargs):
        self._started = False
