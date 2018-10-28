import threading
import time
import queue

from .traffic import GetTraffic, SendTraffic

THREAD_DELAY = 0.001


class SocketThread(threading.Thread):

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
        self.join()

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

    def __repr__(self):
        return "{}({}, qsize={})".format(
            self.__class__.__name__, self.id, self.pending.qsize()
        )


class GetFromThread(GetTraffic, SocketThread):

    def get_update(self):
        return super().get_update(self.socket)

    def execute(self):
        update = self.get_update()
        self.pending.put(update)


class SendToThread(SendTraffic, SocketThread):

    def put(self, data, block=True):
        self.pending.put(data, block=block)

    def execute(self):
        send = self.pending.get()
        self.send_update(send)

    def send_update(self, data):
        super().send_update(self.socket, data)
