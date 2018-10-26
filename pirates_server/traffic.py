import json
import socket
import threading
import time
import queue

FILLER = "^"
INSTRUCTION_LENGTH = 1024
THREAD_DELAY = 0.001


class HandleTraffic:

    def get_socket_pool(self, host, port):
        socket_pool = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_pool.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_pool.bind((host, port))
        socket_pool.listen(5)
        return socket_pool

    def get_socket(self, host, port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        return client_socket

    def get_update(self, socket):
        chunks = []
        bytes_received = 0
        while bytes_received < INSTRUCTION_LENGTH:
            chunk = socket.recv(
                min(INSTRUCTION_LENGTH - bytes_received,
                    INSTRUCTION_LENGTH * 2)
            )
            if chunk == b"":
                raise RuntimeError("Socket is broken on getting!")
            chunks.append(chunk)
            bytes_received = bytes_received + len(chunk)
        bytes_data = b"".join(chunks)
        return self.parse_bytes_to_json(bytes_data)

    def parse_bytes_to_json(self, bytes_data):
        bytes_data = bytes_data.decode().replace(FILLER, "")
        bytes_data = json.loads(bytes_data)
        return bytes_data

    def send_update(self, socket, data):
        if not data:
            data = {"method": "do_nothing", "player_address": None}
        bytes_data = self.parse_json_to_bytes(data)
        bytes_sent = 0
        while bytes_sent < INSTRUCTION_LENGTH:
            sent = socket.send(bytes_data[bytes_sent:])
            if sent == 0:
                raise RuntimeError("Socket is broken on sending!")
            bytes_sent += sent
        return []

    def parse_json_to_bytes(self, json_data):
        json_data = json.dumps(json_data)
        count = (INSTRUCTION_LENGTH - len(json_data)) / 2
        if count.is_integer():
            extra = ""
        else:
            extra = FILLER
        count = int(count)
        filler_bytes = FILLER * count
        bytes_data = (filler_bytes + json_data + filler_bytes + extra).encode()
        return bytes_data

    def execute(self, player_address, method, args=None, kwargs=None):
        method = getattr(self, method)
        args = args or []
        kwargs = kwargs or {}
        method(player_address, *args, **kwargs)


class SocketThread(HandleTraffic, threading.Thread):

    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        _, self.id = socket.getpeername()
        self.pending = queue.Queue()
        self.running = True

    def run(self):
        while self.running:
            self.execute()
            time.sleep(THREAD_DELAY)

    def stop(self):
        self.running = False

    def get(self, block=False):
        try:
            return self.pending.get(block=block)
        except queue.Empty:
            return None

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.pending.get(block=False)
        except queue.Empty:
            raise StopIteration


class GetFromThread(SocketThread):

    def get_update(self):
        return super().get_update(self.socket)

    def execute(self):
        update = self.get_update()
        self.pending.put(update)

    def __repr__(self):
        return "{}({}, qsize={})".format(
            self.__class__.__name__, self.id, self.pending.qsize()
        )


class SendToThread(SocketThread):

    def put(self, data, block=True):
        self.pending.put(data, block=block)

    def execute(self):
        send = self.pending.get()
        self.send_update(send)

    def send_update(self, data):
        super().send_update(self.socket, data)

    def __repr__(self):
        return "{}({}, qsize={})".format(
            self.__class__.__name__, self.id, self.pending.qsize()
        )
