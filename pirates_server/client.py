import socket

from .traffic import HandleTraffic


class Client(HandleTraffic):

    def get_socket(self, host, port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        return client_socket
