import json

from twisted.trial import unittest
from twisted.test import proto_helpers

from networking.server import ServerConnectionFactory


class TwistedHelpers:

    def setUp(self):
        self.factory = ServerConnectionFactory()
        self.proto = self.get_proto()
        self.transport = proto_helpers.StringTransport()
        self.proto.makeConnection(self.transport)

    def get_proto(self):
        return self.factory.buildProtocol(("127.0.0.1", 5000))

    def get_transport(self):
        return proto_helpers.StringTransport()


class ServerConnectionGameSetupTests(TwistedHelpers, unittest.TestCase):

    def test_make_admin_if_first_connected(self):
        self.assertTrue(self.proto.is_admin)

    def test_not_admin_if_not_first_connected(self):
        new_proto = self.get_proto()
        new_transport = self.get_transport()
        new_proto.makeConnection(new_transport)
        self.assertFalse(new_proto.is_admin)

    def test_connecting_to_server_returns_player_token(self):
        token = json.loads(self.transport.value())["token"]
        self.assertEqual(token, self.proto.token, token)

    def test_team_assignment_alternates_between_connecting_players(self):
        new_proto = self.get_proto()
        new_transport = self.get_transport()
        new_proto.makeConnection(new_transport)
        first_team, second_team = [
            p["team"] for p in self.proto.player_data.values()]
        self.assertNotEqual(first_team, second_team)

    def test_starting_x_and_y_changes_between_connection_players(self):
        new_proto = self.get_proto()
        new_transport = self.get_transport()
        new_proto.makeConnection(new_transport)
        first_pos, second_pos = [(p["x"], p["y"])
                                 for p in self.proto.player_data.values()]
        self.assertNotEqual(first_pos, second_pos)

    def test_admin_can_start_game(self):
        instruction = json.dumps({"start_game": True}) + "\r\n"
        self.proto.dataReceived(instruction.encode())
        self.assertTrue(self.proto.started)

    def test_non_admin_cannot_start_game(self):
        new_proto = self.get_proto()
        new_transport = self.get_transport()
        new_proto.makeConnection(new_transport)
        instruction = json.dumps({"start_game": True}) + "\r\n"
        new_proto.dataReceived(instruction.encode())
        self.assertFalse(new_proto.started)

    def test_admin_starting_game_starts_game_on_other_connections(self):
        new_proto = self.get_proto()
        new_transport = self.get_transport()
        new_proto.makeConnection(new_transport)
        instruction = json.dumps({"start_game": True}) + "\r\n"
        self.proto.dataReceived(instruction.encode())
        self.assertTrue(new_proto.started)

    def test_starting_game_sends_player_data_to_clients(self):
        self.transport.clear()
        instruction = json.dumps({"start_game": True}) + "\r\n"
        self.proto.dataReceived(instruction.encode())
        response = self.transport.value().decode()
        data = json.loads(response)
        self.assertEqual(data, self.proto.player_data)


class ServerConnectionSendInstructionsTests(TwistedHelpers, unittest.TestCase):

    def test_received_instruction_sent_to_other_clients(self):
        self.proto.start_game()
        new_proto = self.get_proto()
        new_transport = self.get_transport()
        new_proto.makeConnection(new_transport)
        new_proto.start_game()
        new_transport.clear()
        instruction = json.dumps({"hello": "world",
                                  "token": self.proto.token}) + "\r\n"
        self.proto.dataReceived(instruction.encode())
        response = new_transport.value().decode()
        data = json.loads(response)
        self.assertEqual(data, {"hello": "world", "token": self.proto.token})

    def test_received_instruction_not_sent_back_to_same_client(self):
        self.proto.start_game()
        self.transport.clear()
        instruction = json.dumps({"hello": "world",
                                  "token": self.proto.token}) + "\r\n"
        self.proto.dataReceived(instruction.encode())
        response = self.transport.value().decode()
        self.assertEqual(response, "")
