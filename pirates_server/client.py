import socket

from .traffic import HandleTraffic


class Client(HandleTraffic):

    def __init__(self, host="localhost", port=5000):
        self.socket = self._get_socket(host, port)
        self._send = []

    def _get_socket(self, host, port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        return client_socket
