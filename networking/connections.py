import json
import secrets

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver

MAX_X = 100


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
        self.sendLine(json.dumps({"token": self.token}).encode())

    def generate_token(self):
        return secrets.token_urlsafe(64)

    def new_player(self):
        num_players = len(self.player_data)
        if num_players % 2:
            team = "pirates"
        else:
            team = "cowboys"
        x_diff = 20 * num_players
        if team == "pirates":
            start_x = x_diff
        else:
            start_x = MAX_X - x_diff
        return {
            "is_admin": self.is_admin,
            "start_x": start_x,
            "start_y": 0,
            "team": team,
            "health": 30,
            "active": True,
        }

    def lineReceived(self, line):
        self.state(line)

    def accepting_players(self, line):
        instruction = json.loads(line)
        if instruction["start_game"] and self.is_admin:
            for _, connection in self.player_connections.items():
                connection.start_game()
            self.send_instruction(self.player_data)

    def start_game(self):
        self.started = True
        self.state = self.accepting_instructions

    def send_instruction(self, instruction, skip=None):
        for token, connection in self.player_connections.items():
            if token == skip:
                continue
            else:
                instruction = json.dumps(instruction)
                connection.sendLine(instruction.encode())

    def accepting_instructions(self, line):
        instruction = json.loads(line)
        token = instruction["player"]
        self.send_instruction(instruction, skip=token)

    def connectionLost(self, reason):
        pass


class ServerConnectionFactory(Factory):

    def __init__(self):
        self.player_data = {}
        self.player_connections = {}

    def buildProtocol(self, addr):
        return ServerConnection(self.player_data, self.player_connections)
