import logging

import tornadoredis
import tornado.web

from chapstream import config
from chapstream import helpers
from chapstream.api import CsWebSocketHandler

logger = logging.getLogger(__name__)


class RealtimeHandler(CsWebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(RealtimeHandler, self).__init__(*args, **kwargs)
        self.listen()

    @tornado.web.authenticated
    @tornado.gen.engine
    def listen(self):
        logger.info('WebSocket opened.')
        self.client = tornadoredis.Client(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            selected_db=config.REDIS_DB
        )
        self.channel = helpers.user_channel(self.current_user.id)
        self.client.connect()
        yield tornado.gen.Task(self.client.subscribe, self.channel)
        self.client.listen(self.on_message)

    @tornado.web.authenticated
    def on_message(self, msg):
        if msg.kind == 'message':
            logger.info('Sending a message via websocket: %s', msg.body)
            self.write_message(str(msg.body))
        if msg.kind == 'disconnect':
            logger.info('Disconnecting from channel: %s', msg.pattern)
            # Do not try to reconnect, just send a message back
            # to the client and close the client connection
            self.write_message('The connection terminated '
                               'due to a Redis server error.')
            self.close()

    @tornado.web.authenticated
    def on_close(self):
        if self.client.subscribed:
            logger.info('WebSocket closed.')
            self.client.unsubscribe(self.channel)
            self.client.disconnect()
