"""
Some wrappers around a Redis pubsub to make it work a little more nicely with
the Server Sent Events API in modern browsers.

To send a message:
import redis
from vr.events import Sender

r = redis.Redis()
sender = Sender(r, channel='foo')
sender.publish('this is my message')


And to listen to messages:
import redis
from vr.events import Listener
r = redis.Redis()
listener = Listener(r, channels=['foo'])
for message in listener:
    do_something(message)

"""

import json
import uuid

import six
import redis

from vr.common import utils


class Sender(object):
    def __init__(self, rcon_or_url, channel, buffer_key=None,
                 buffer_length=100):
        if isinstance(rcon_or_url, redis.StrictRedis):
            self.rcon = rcon_or_url
        elif isinstance(rcon_or_url, six.string_types):
            self.rcon = redis.StrictRedis(**utils.parse_redis_url(rcon_or_url))
        self.channel = channel
        self.buffer_key = buffer_key
        self.buffer_length = buffer_length

    def publish(self, data, msgid=None, event=None):
        message = self.format(data, msgid, event)

        # Serialize it and stick it on the pubsub
        self.rcon.publish(self.channel, message)

        # Also stick it on the end of our length-capped list, so consumers can
        # get a list of recent events as well as seeing current ones.
        if self.buffer_key:
            self.rcon.lpush(self.buffer_key, message)
            self.rcon.ltrim(self.buffer_key, 0, self.buffer_length - 1)

    def flush(self):
        self.rcon.publish(self.channel, 'flush')

    def format(self, data, msgid=None, event=None):
        out = {
            'id': msgid or uuid.uuid1().hex,
            'data': data,
        }

        if event:
            out['event'] = event
        return json.dumps(out)

    def close(self):
        self.rcon.connection_pool.disconnect()


class Listener(object):
    def __init__(self, rcon_or_url, channels, buffer_key=None,
                 last_event_id=None):
        if isinstance(rcon_or_url, redis.StrictRedis):
            self.rcon = rcon_or_url
        elif isinstance(rcon_or_url, six.string_types):
            self.rcon = redis.StrictRedis(**utils.parse_redis_url(rcon_or_url))
        self.channels = channels
        self.buffer_key = buffer_key
        self.last_event_id = last_event_id
        self.pubsub = self.rcon.pubsub()
        self.pubsub.subscribe(channels)

        self.ping()

    def __iter__(self):
        # If we've been initted with a buffer key, then get all the events off
        # that and spew them out before blocking on the pubsub.

        for msg in self.get_buffer():
            parsed = json.loads(msg)
            # account for earlier version that used 'message'
            data = parsed.get('data') or parsed.get('message')
            yield self.format(data, msgid=parsed['id'],
                              event=parsed.get('event'))

        for msg in self.pubsub.listen():
            # pubsub msg will be a dict with keys 'pattern', 'type', 'channel',
            # and 'data'
            if msg['type'] == 'message':
                if msg['data'] == 'flush':
                    yield ':\n'
                else:
                    parsed = json.loads(msg['data'])
                    yield self.format(parsed['data'], msgid=parsed['id'],
                                      event=parsed.get('event'))

    def ping(self):
        # Send a superfluous message down the pubsub to flush out stale
        # connections.
        for channel in self.channels:
            # Use buffer_key=None since these pings never need to be remembered
            # and replayed.
            sender = Sender(self.rcon, channel, buffer_key=None)
            sender.flush()

    def get_buffer(self):
        # Only return anything from buffer if we've been given a last event ID
        if not self.buffer_key:
            return []

        buffered_events = self.rcon.lrange(self.buffer_key, 0, -1)

        # check whether msg with last_event_id is still in buffer.  If so,
        # trim buffered_events to have only newer messages.
        if self.last_event_id:
            # Note that we're looping through most recent messages first,
            # here
            counter = 0
            for msg in buffered_events:
                if (json.loads(msg)['id'] == self.last_event_id):
                    break
                counter += 1
            buffered_events = buffered_events[:counter]

        # Return oldest messages first
        return reversed(list(buffered_events))

    def format(self, data, msgid=None, retry=None, event=None):

        out = ''

        if msgid:
            out += 'id: %s\n' % msgid
        if retry:
            out += 'retry: %s\n' % retry
        if event:
            out += 'event: %s\n' % event

        # data comes last.  It may be str or an iterable representing multiple
        # lines
        if isinstance(data, six.string_types):
            out += 'data: %s\n' % data
        else:
            out += '\n'.join('data: %s' % l for l in data) + '\n'
        out += '\n'
        return out

    def close(self):
        self.rcon.connection_pool.disconnect()
