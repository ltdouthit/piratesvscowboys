import json
import secrets

from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver

MAX_X = 500


class ServerConnection(LineReceiver):

    def __init__(self, player_data, player_connections):
        self.player_data = player_data
        self.player_connections = player_connections
        self.is_admin = False
        self.token = None
        self.started = False
        self.finished = False
        self.state = self.accepting_players

    def connectionMade(self):
        self.token = self.generate_token()
        if not self.player_connections:
            self.is_admin = True
        new_player_data = self.new_player()
        self.player_connections[self.token] = self
        self.player_data[self.token] = new_player_data
        self.sendLine(json.dumps(
            {"token": self.token,
             "is_admin": self.is_admin}
        ).encode())

    def generate_token(self):
        return secrets.token_urlsafe(64)

    def new_player(self):
        num_players = len(self.player_data)
        if num_players % 2:
            team = "pirates"
        else:
            team = "cowboys"
        x_diff = 10 * num_players
        if team == "pirates":
            start_x = x_diff
        else:
            start_x = MAX_X - x_diff
        return {
            "x": start_x,
            "y": 0,
            "team": team,
            "health": 30,
            "active": True,
        }

    def lineReceived(self, line):
        self.state(line)

    def accepting_players(self, line):
        try:
            instruction = json.loads(line)[0]
        except KeyError:
            instruction = json.loads(line)
        if instruction["start_game"] and self.is_admin:
            for _, connection in self.player_connections.items():
                connection.start_game()

    def start_game(self):
        self.started = True
        self.state = self.accepting_instructions
        self.sendLine(json.dumps(self.player_data).encode())

    def send_instruction(self, instruction, skip=None):
        for token, connection in self.player_connections.items():
            if token == skip:
                continue
            else:
                instruction = json.dumps(instruction)
                connection.sendLine(instruction.encode())

    def accepting_instructions(self, line):
        instructions = json.loads(line)
        if not isinstance(instructions, list):
            instructions = [instructions]
        for ins in instructions:
            print("Sending instruction: {}".format(ins))
            token = ins["token"]
            self.send_instruction(ins, skip=token)

    def connectionLost(self, reason):
        pass


class ServerConnectionFactory(Factory):

    def __init__(self):
        self.player_data = {}
        self.player_connections = {}

    def buildProtocol(self, addr):
        print("Connecting user: {}".format(addr))
        return ServerConnection(self.player_data, self.player_connections)


class Server:

    def __init__(self, port, server_reactor=reactor):
        self.port = port
        self.reactor = server_reactor
        self.factory = ServerConnectionFactory()

    def run(self):
        print("Starting server on port {}".format(self.port))
        self.reactor.listenTCP(self.port, self.factory)
        self.reactor.run()
