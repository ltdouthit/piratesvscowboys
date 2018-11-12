import json

from twisted.trial import unittest
from twisted.test import proto_helpers

from networking.client import IterableQueue, PlayerConnection, Client


class IterableQueueTests(unittest.TestCase):

    def setUp(self):
        self.it = IterableQueue()

    def test_sanity(self):
        self.assertTrue(self.it)

    def test_iterate(self):
        self.it.put("hello")
        self.it.put("world")
        results = [i for i in self.it]
        self.assertEqual(results, ["hello", "world"])


class PlayerConnectionTests(unittest.TestCase):

    def setUp(self):
        self.transport = proto_helpers.StringTransport()
        gf = IterableQueue()
        st = IterableQueue()
        self.proto = PlayerConnection(gf, st)
        self.proto.makeConnection(self.transport)

    def test_received_data_adds_to_queue(self):
        instruction = json.dumps({"hello": "world"}) + "\r\n"
        self.proto.dataReceived(instruction.encode())
        data = self.proto.get_from.get()
        self.assertEqual(data, {"hello": "world"})

    def test_send_local_instructions(self):
        instructions = [{"hello": "world"}, {"goodbye": "void"}]
        for i in instructions:
            self.proto.send_to.put(i)
        self.proto.send_local_instructions()
        response = self.transport.value().decode()
        response_data = json.loads(response)
        self.assertEqual(response_data, instructions)


class ClientTests(unittest.TestCase):

    def setUp(self):
        self.client = Client("localhost", 5000,
                             client_reactor=proto_helpers.MemoryReactor)

    def test_sanity(self):
        self.assertTrue(self.client)

    def test_property_remote_instructions(self):
        self.client.get_from.put("hello")
        self.client.get_from.put("world")
        self.assertEqual(self.client.remote_instructions, ["hello", "world"])

    def test_send_local_instructions_consumes_queue(self):
        self.client.factory.buildProtocol(None)
        transport = proto_helpers.StringTransport()
        self.client.factory.connection.makeConnection(transport)
        self.client.send_to.put({"hello": "world"})
        self.client.send_to.put({"goodbye": "void"})
        self.client.send_local_instructions()
        self.assertIsNone(self.client.send_to.get())
