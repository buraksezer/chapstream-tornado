import json
import logging

import redis
from kuyruk import Kuyruk

from chapstream import config
from chapstream.config import task_queue
from chapstream.backend.db import session
from chapstream.backend.db.models.user import User, UserRelation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

kuyruk = Kuyruk(config.task_queue)


def push_to_timeline(user, post):
    # TODO: Connection pool?
    redis_conn = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT
    )
    try:
        channel = str(user.id) + '_channel'
        timeline = str(user.id) + '_timeline'
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


# TODO: Add retry
@kuyruk.task
def post_timeline(post):
    owner = User.get(post['user_id'])
    push_to_timeline(owner, post)

    relations = session.query(UserRelation).\
        filter_by(chap_id=post['user_id'], is_banned=False).all()

    for relation in relations:
        user = User.get(relation.user_id)
        if not user:
            logger.info("User could not be found: %s", user.name)
            continue
        push_to_timeline(user, post)


@kuyruk.task
def block_user(user_id, chap_id):
    user = User.get(user_id)
    chap = User.get(chap_id)

    if not user or not chap:
        logger.error("Users could not be found: User:%s Blocked:%s" %
                     (user_id, chap_id))
        return

    redis_conn = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT
    )

    def remove_posts(timeline, blocked_user):
        length = redis_conn.llen(timeline)
        posts = redis_conn.lrange(timeline, 0, length)
        for post in posts:
            parsed = json.loads(post)
            if parsed["user_id"] == blocked_user.id:
                logger.info("Remove post from: %s. Post: %s"
                            % (blocked_user.name, post))
                redis_conn.lrem(timeline, post)

    # Remove posts from the user who blocks a user.
    user_timeline = str(user.id) + '_timeline'
    remove_posts(user_timeline, chap)

    # Remove posts from the blocked user.
    chap_timeline = str(chap.id) + '_timeline'
    remove_posts(chap_timeline, user)

