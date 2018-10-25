import socket

from traffic import HandleTraffic, GetFromThread, SendToThread


HOST = ""
PORT = 5000


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
            player_socket, player_address = self._socket_pool.accept()
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
