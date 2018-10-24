import json
import unittest

from pirates_server.traffic import (
    HandleTraffic,
    FILLER, INSTRUCTION_LENGTH, DO_NOTHING_INSTRUCTION
)

from pirates_server.server import PVCS


class MockSocket:

    def __init__(self, return_value=None):
        self.return_value = return_value
        self.bytes_sent = 0
        self.data_sent = b""

    def recv(self, *args, **kwargs):
        return self.return_value

    def send(self, data):
        self.bytes_sent = len(data)
        self.data_sent = data
        return len(data)


class HandleTrafficTests(unittest.TestCase):

    def setUp(self):
        self.handler = HandleTraffic()

    def test_get_update_do_nothing(self):
        socket = MockSocket(DO_NOTHING_INSTRUCTION)
        update = self.handler.get_update(socket)
        self.assertIsNone(update)

    def test_get_update_on_dict(self):
        return_value = json.dumps({"hello": "world"})
        return_value += (FILLER * (INSTRUCTION_LENGTH - len(return_value)))
        return_value = return_value.encode()
        socket = MockSocket(return_value)
        update = self.handler.get_update(socket)
        self.assertEqual(update, {"hello": "world"})

    def test_send_update_depletes_data(self):
        socket = MockSocket()
        data = [{"hello": "world"}]
        data = self.handler.send_update(socket, data)
        self.assertEqual(data, [])

    def test_send_update_even_length_sends_correct_length(self):
        socket = MockSocket()
        data = [{"hello": "world"}]
        self.handler.send_update(socket, data)
        self.assertEqual(socket.bytes_sent, INSTRUCTION_LENGTH)

    def test_send_updates_odd_length_sends_correct_length(self):
        socket = MockSocket()
        data = [{"goodbye": "dramas"}]
        self.handler.send_update(socket, data)
        self.assertEqual(socket.bytes_sent, INSTRUCTION_LENGTH)

    def test_send_updates_no_data_sends_do_nothing(self):
        socket = MockSocket()
        data = []
        self.handler.send_update(socket, data)
        self.assertEqual(socket.data_sent, DO_NOTHING_INSTRUCTION)


class PVCSTests(unittest.TestCase):

    def setUp(self):
        self.pvcs = PVCS()

    def test_execute_calls_method(self):
        instruction = {"method": "quit"}
        self.pvcs.execute(1, **instruction)
        self.assertFalse(self.pvcs._started)


if __name__ == "__main__":
    unittest.main()
