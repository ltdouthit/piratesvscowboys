import unittest

from mock import Mock, patch

from pirates_vs_cowboys.items import Agent, Bullet, BaseItem, Crate, Treasure
from pirates_vs_cowboys.items import (
    agent_team_images, VELOCITY_DECAY, MIN_X, MAX_X, MIN_Y, MAX_Y, AGENT_SPEED, BULLET_SPEED
)


def get_mock_object(x=5, y=5, width=1, height=1, **kwargs):
    m = Mock()
    m.configure_mock(x=x, y=y, width=width, height=height, **kwargs)
    return m


class BaseItemTests(unittest.TestCase):

    def setUp(self):
        self.item = BaseItem(5, 5, width=2, height=2)

    @patch("pirates_vs_cowboys.items.BaseItem.handle_collision")
    def test_check_and_handle_collision_when_collided(self, collision):
        obj = get_mock_object(x=5, y=5, width=1, height=1)
        self.item.check_and_handle_collision(obj)
        self.assertTrue(collision.called)

    @patch("pirates_vs_cowboys.items.BaseItem.handle_collision")
    def test_check_and_handle_collision_when_not_collided(self, collision):
        obj = get_mock_object(x=1, y=1)
        self.item.check_and_handle_collision(obj)
        self.assertFalse(collision.called)


class CrateTests(unittest.TestCase):

    def setUp(self):
        self.crate = Crate(5, 5, width=2, height=2)

    def test_check_and_handle_collision_obj_above(self):
        obj = get_mock_object(x=5, y=4, width=1, height=1, speed=2, y_vel=0)
        self.crate.check_and_handle_collision(obj)
        self.assertEqual(obj.y_vel, -1)

    def test_check_and_handle_collision_obj_right(self):
        obj = get_mock_object(x=6, y=5, width=1, height=1, speed=2, x_vel=0)
        self.crate.check_and_handle_collision(obj)
        self.assertEqual(obj.x_vel, 1)

    def test_check_and_handle_collision_obj_below(self):
        obj = get_mock_object(x=5, y=6, width=1, height=1, speed=2, y_vel=0)
        self.crate.check_and_handle_collision(obj)
        self.assertEqual(obj.y_vel, 1)

    def test_check_and_handle_collision_obj_left(self):
        obj = get_mock_object(x=4, y=5, width=1, height=1, speed=2, x_vel=0)
        self.crate.check_and_handle_collision(obj)
        self.assertEqual(obj.x_vel, -1)


class TreasureTests(unittest.TestCase):

    def setUp(self):
        self.treasure = Treasure("cowboys", 5, 5, width=2, height=2)

    @patch("pirates_vs_cowboys.items.Treasure.handle_collision")
    def test_check_and_handle_collision_not_held_yet_gets_picked_up(self, collision):
        obj = get_mock_object(picked_up=None)
        self.treasure.check_and_handle_collision(obj)
        self.assertTrue(collision.called)

    @patch("pirates_vs_cowboys.items.Treasure.handle_collision")
    def test_check_and_handle_collision_already_held_does_not_get_picked_up(self, collision):
        obj = get_mock_object(picked_up=None)
        self.treasure.held_by = obj
        self.treasure.check_and_handle_collision(obj)
        self.assertFalse(collision.called)

    @patch("pirates_vs_cowboys.items.Treasure.handle_collision")
    def test_check_and_handle_collision_agent_already_picked_up_item(self, collision):
        obj = get_mock_object(picked_up=["other thing"])
        self.treasure.check_and_handle_collision(obj)
        self.assertFalse(collision.called)

    def test_handle_collision_gets_picked_up_and_held_by_agent(self):
        obj = get_mock_object(picked_up=[])
        self.treasure.handle_collision(obj)
        self.assertEqual(obj.picked_up, [self.treasure])
        self.assertEqual(self.treasure.held_by, obj)

    def test_handle_collision_winner(self):
        other_treasure = Treasure("pirates", 10, 10)
        obj = get_mock_object(team="cowboys", picked_up=[other_treasure], won=False)
        self.treasure.handle_collision(obj)
        self.assertTrue(obj.won)

    def test_move_when_not_held(self):
        old_x, old_y = self.treasure.x, self.treasure.y
        self.treasure.move()
        self.assertEqual(self.treasure.x, old_x)
        self.assertEqual(self.treasure.y, old_y)

    def test_move_when_held_matches_carrier(self):
        obj = get_mock_object()
        self.treasure.held_by = obj
        obj.x = 500
        obj.y = 500
        self.treasure.move()
        self.assertEqual(self.treasure.x, obj.x - 5)
        self.assertEqual(self.treasure.y, obj.y)


team_image_data = agent_team_images["cowboys"]


class AgentTests(unittest.TestCase):

    def setUp(self):
        self.agent = Agent(team="cowboys", x=5, y=5)

    def test_image_data_property_moving_right(self):
        self.agent.x_vel = 1
        self.assertEqual(self.agent.image_data, team_image_data["right"])

    def test_image_data_property_moving_left(self):
        self.agent.x_vel = 0.0001
        self.assertEqual(self.agent.image_data, team_image_data["left"])

    def test_change_velocity_does_change_velocity(self):
        self.agent.x_vel = 0
        self.agent.change_velocity(x=1)
        self.assertEqual(self.agent.x_vel, 1)

    def test_change_velocity_does_not_change_other_velocity(self):
        self.agent.x_vel = 0
        self.agent.y_vel = 0
        self.agent.change_velocity(y=1)
        self.assertEqual(self.agent.x_vel, 0)

    def test_move_applies_velocity(self):
        x_vel, y_vel = 1, 2
        self.agent.x_vel, self.agent.y_vel = x_vel, y_vel
        self.agent.y = MAX_Y
        old_x, old_y = self.agent.x, self.agent.y
        self.agent.move()
        self.assertEqual(self.agent.x, old_x + x_vel)
        self.assertEqual(self.agent.y, old_y + y_vel)

    def test_move_decays_velocity(self):
        x_vel, y_vel = 1, 2
        self.agent.x_vel, self.agent.y_vel = x_vel, y_vel
        self.agent.y = MAX_Y
        self.agent.move()
        self.assertEqual(self.agent.x_vel, x_vel * VELOCITY_DECAY)
        self.assertEqual(self.agent.y_vel, y_vel * VELOCITY_DECAY)

    def test_move_x_too_low(self):
        self.agent.x = MIN_X - 1
        self.agent.move()
        self.assertEqual(self.agent.x, MIN_X - 1 + AGENT_SPEED)

    def test_move_x_too_high(self):
        self.agent.x = MAX_X + 1
        self.agent.move()
        self.assertEqual(self.agent.x, MAX_X + 1 - AGENT_SPEED)

    def test_move_y_too_high(self):
        self.agent.y = MAX_Y + 1
        self.agent.move()
        self.assertEqual(self.agent.y, MAX_Y)

    def test_move_brings_player_towards_ground_if_above_ground(self):
        self.agent.y = MAX_Y - 100
        old_y = self.agent.y
        self.agent.move()
        self.assertEqual(self.agent.y, old_y + int(AGENT_SPEED / 2))

    def test_move_y_too_low(self):
        self.agent.y = MIN_Y - 1
        self.agent.move()
        self.assertEqual(self.agent.y, MIN_Y - 1 + AGENT_SPEED)

    def test_has_enemy_treasure_property_does_have_it(self):
        treasure = Treasure(team="pirates", x=5, y=5)
        self.agent.picked_up = [treasure]
        self.assertTrue(self.agent.has_enemy_treasure)

    def test_has_enemy_treasure_property_has_same_team_treasure(self):
        treasure = Treasure(team="cowboys", x=5, y=5)
        self.agent.picked_up = [treasure]
        self.assertFalse(self.agent.has_enemy_treasure)

    def test_has_enemy_treasure_property_has_some_other_enemy_team_item(self):
        obj = get_mock_object(team="pirates")
        self.agent.picked_up = [obj]
        self.assertFalse(self.agent.has_enemy_treasure)


class BulletTests(unittest.TestCase):

    def setUp(self):
        self.bullet = Bullet(team="cowboys", facing=0, x=5, y=5)

    def test_move_facing_right(self):
        old_x = self.bullet.x
        self.bullet.facing = 0
        self.bullet.move()
        self.assertEqual(self.bullet.x, old_x + BULLET_SPEED)

    def test_move_facing_left(self):
        old_x = self.bullet.x
        self.bullet.facing = 1
        self.bullet.move()
        self.assertEqual(self.bullet.x, old_x - BULLET_SPEED)

    @patch("pirates_vs_cowboys.items.Bullet.handle_collision")
    def test_check_and_handle_collision_does_not_collide(self, collision):
        obj = get_mock_object(x=1, y=1)
        self.bullet.check_and_handle_collision(obj)
        self.assertFalse(collision.called)

    @patch("pirates_vs_cowboys.items.Bullet.handle_collision")
    def test_check_and_handle_collision_does_collide_same_team(self, collision):
        obj = get_mock_object(x=1, y=1, team="cowboys")
        self.bullet.check_and_handle_collision(obj)
        self.assertFalse(collision.called)

    def test_check_and_handle_collision_does_collide_different_team(self):
        obj = get_mock_object(x=5, y=5, team="pirates", health=10)
        self.bullet.check_and_handle_collision(obj)
        self.assertEqual(obj.health, 10 - self.bullet.damage)
        self.assertFalse(self.bullet.active)
