"""Unit tests for :class:`vr.events.Listener`."""
import unittest

from mock import MagicMock, patch

from vr.events import Listener


class MockRedis(MagicMock):
    pass


class ListenerTestCase(unittest.TestCase):

    def test_create_listener(self):
        with patch('redis.StrictRedis', MockRedis):
            listener = Listener('redis://localhost:6379/0', channels=['foo'])

        self.assertIsInstance(listener.rcon, MockRedis)
        self.assertEqual(listener.channels, ['foo'])
