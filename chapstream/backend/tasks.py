import json
import logging

import redis
from kuyruk import Kuyruk

from chapstream import config
from chapstream.config import task_queue
from chapstream.backend.db import session
from chapstream.backend.db.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

kuyruk = Kuyruk(config.task_queue)


# TODO: Add retry
@kuyruk.task
def post_timeline(post):
    # TODO: Connection pool?
    redis_conn = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT
    )
    try:
        # Add the post user's timeline
        users = ['burak', 'remzi']
        for user in users:
            chap = session.query(User).filter_by(
                name=user).first()
            if not chap:
                logger.info("User could not be found: %s", user)
                continue
            channel = str(chap.id) + '_channel'
            timeline = str(chap.id) + '_timeline'
            post = json.dumps(post)
            # Push user's timeline the current post
            redis_conn.rpush(timeline, post)
            # TODO: Check size of the list and rotate it if
            # required.
            logger.info('Sending a message to %s', channel)
            redis_conn.publish(channel, post)
    except redis.ConnectionError as err:
        logger.error('Connection error: %s', err)
        # TODO: Handle failed tasks

