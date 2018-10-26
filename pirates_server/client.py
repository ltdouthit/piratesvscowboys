import socket

from .traffic import GetTraffic


class Client(GetTraffic):

    def get_socket(self, host, port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        return client_socket

    def execute_remote_instruction(self, player_address, method,
                                   args=None, kwargs=None):
        method = getattr(self, method)
        args = args or []
        kwargs = kwargs or {}
        method(player_address, *args, **kwargs)
