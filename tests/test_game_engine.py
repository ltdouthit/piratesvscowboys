import unittest

from collections import UserList

from mock import Mock

from pirates_vs_cowboys.game import Game
from pirates_vs_cowboys.game import SCREEN_X


class MockQueue(UserList):

    def put(self, value):
        self.data.append(value)


class MockClient:

    def __init__(self):
        self.send_to = MockQueue()
        self.remote_instructions = []

    def send_local_instructions(self):
        pass


class MockPyxel:
    KEY_D = "D"
    KEY_A = "A"
    KEY_SPACE = " "
    KEY_Q = "Q"
    KEY_F = "F"

    def __init__(self):
        self.key_pressed = None
        self.has_quit = False
        self.drawn_to_screen = []

    def btnp(self, key):
        return key == self.key_pressed

    def quit(self):
        self.has_quit = True

    def blt(self, *args):
        self.drawn_to_screen.append(args)


class SetupMocks:

    def setUp(self):
        self.mock_client = MockClient()
        self.mock_pyxel = MockPyxel()
        self.token = "SETEC_ASTRO1"
        self.game_state = {
            "SETEC_ASTRO1": {
                "team": "cowboys",
                "x": 5,
                "y": 10,
            },
            "SETEC_ASTRO2": {
                "team": "pirates",
                "health": 40,
                "x": 10,
                "y": 15,
            }
        }

    def get_game(self):
        return Game(client=self.mock_client, game_state=self.game_state,
                    token=self.token, game_pyxel=self.mock_pyxel)

    def get_mock_item(self, render_method="blt", **kwargs):
        m = Mock()
        m.configure_mock(render_method=render_method, **kwargs)
        return m


class GameEngineSetupTests(SetupMocks, unittest.TestCase):

    def test_get_players_from_game_state(self):
        game = self.get_game()
        p1 = game.players["SETEC_ASTRO1"]
        p2 = game.players["SETEC_ASTRO2"]
        self.assertEqual(p1.team, "cowboys")
        self.assertEqual(p1.health, 30)
        self.assertEqual(p1.x, 5)
        self.assertEqual(p1.y, 10)
        self.assertEqual(p2.team, "pirates")
        self.assertEqual(p2.health, 40)
        self.assertEqual(p2.x, 10)
        self.assertEqual(p2.y, 15)


class GameEngineUpdateTests(SetupMocks, unittest.TestCase):

    def test_get_local_move_returns_instructions_if_key_pressed(self):
        game = self.get_game()
        self.mock_pyxel.key_pressed = self.mock_pyxel.KEY_D
        self.assertIsInstance(game.get_keyboard_move(), dict)

    def test_get_local_move_returns_nothing_if_no_key_pressed(self):
        game = self.get_game()
        self.mock_pyxel.key_pressed = None
        self.assertIsNone(game.get_keyboard_move())

    def test_local_move_added_to_queue_of_instructions_to_send_out(self):
        game = self.get_game()
        self.mock_pyxel.key_pressed = self.mock_pyxel.KEY_D
        game.update()
        self.assertEqual(len(self.mock_client.send_to), 1)

    def test_remote_instructions_are_executed(self):
        self.mock_client.remote_instructions = [{"method": "player_quit"}]
        game = self.get_game()
        game.update()
        self.assertTrue(self.mock_pyxel.has_quit)


class GameEngineDrawTests(SetupMocks, unittest.TestCase):

    def test_draw_item_is_not_drawn_if_off_screen(self):
        game = self.get_game()
        item = self.get_mock_item(x=500)
        game.draw_item(item)
        self.assertEqual(self.mock_pyxel.drawn_to_screen, [])

    def test_draw_item_is_drawn_if_not_off_screen(self):
        game = self.get_game()
        item = self.get_mock_item(x=game.local_player.x + 5, y=5, image_data=["image data"])
        game.draw_item(item)
        self.assertEqual(self.mock_pyxel.drawn_to_screen, [(SCREEN_X + 5, 5, "image data")])
