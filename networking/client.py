import json
import queue

from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver


class IterableQueue:

    def __init__(self):
        self.pending = queue.Queue()

    def get(self, block=False):
        try:
            return self.pending.get(block=block)
        except queue.Empty:
            return

    def put(self, item):
        self.pending.put(item)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.pending.get(block=False)
        except queue.Empty:
            raise StopIteration


class PlayerConnection(LineReceiver):

    def __init__(self, get_from, send_to):
        self.get_from = get_from
        self.send_to = send_to

    def lineReceived(self, line):
        data = json.loads(line.decode())
        self.get_from.put(data)

    def send_local_instructions(self):
        instructions = [ins for ins in self.send_to]
        instructions = json.dumps(instructions)
        self.sendLine(instructions.encode())


class PlayerConnectionFactory(protocol.ClientFactory):

    def __init__(self, get_from, send_to):
        self.get_from = get_from
        self.send_to = send_to
        self.connection = None

    def buildProtocol(self, _):
        self.connection = PlayerConnection(self.get_from, self.send_to)
        return self.connection


class Client:

    def __init__(self, host, port, client_reactor=reactor):
        self.host = host
        self.port = port
        self.reactor = client_reactor
        self.get_from = IterableQueue()
        self.send_to = IterableQueue()
        self.factory = PlayerConnectionFactory(self.get_from, self.send_to)
        self.running = True

    def run(self):
        print("Connecting client to {}:{}".format(self.host, self.port))
        self.reactor.connectTCP(self.host, self.port, self.factory)
        self.reactor.run()

    @property
    def remote_instructions(self):
        return [ins for ins in self.get_from]

    def send_local_instructions(self):
        self.factory.connection.send_local_instructions()

    def stop(self):
        self.reactor.callFromThread(self.reactor.stop)
