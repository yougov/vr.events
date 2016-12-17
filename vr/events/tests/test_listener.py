"""Unit tests for :class:`vr.events.Listener`."""
from unittest.mock import MagicMock, patch

from vr.events import Listener


class MockRedis(MagicMock):
    pass


class TestListener:

    def test_create_listener(self):
        with patch('redis.StrictRedis', MockRedis):
            listener = Listener('redis://localhost:6379/0', channels=['foo'])

        assert isinstance(listener.rcon, MockRedis)
        assert listener.channels == ['foo']
