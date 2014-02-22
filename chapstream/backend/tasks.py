import json
import logging

import redis
from kuyruk import Kuyruk

from chapstream import config
from chapstream.redisconn import redis_conn
from chapstream.config import task_queue
from chapstream import helpers
from chapstream.backend.db import session
from chapstream.backend.db.models.user import User, UserRelation
from chapstream.backend.db.models.group import Group
from chapstream.backend.db.models.notification import Notification


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

kuyruk = Kuyruk(config.task_queue)


def push_to_timeline(user, post):
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
def post_timeline(post, receiver_users=None, receiver_groups=None):
    if not receiver_groups:
        owner = User.get(post['user_id'])
        push_to_timeline(owner, post)

    relations = session.query(UserRelation).\
        filter_by(chap_id=post['user_id'], is_banned=False).all()

    if receiver_groups:
        # Push this post to member of the groups
        for group_id in receiver_groups:
            post_to_group(group_id, post)

    for relation in relations:
        group_receiver = False
        user = User.get(relation.user_id)
        if not user:
            logger.info("User could not be found: %s", user.name)
            continue

        if receiver_groups:
            # If the user is a member of the receiver groups,
            # dont send the post to the user directly
            for group_id in receiver_groups:
                user_key = str(user.id)
                if redis_conn.sismember(user_key, group_id):
                    group_receiver = True
                    break

        if group_receiver:
            continue

        if receiver_users:
            if not user.name in receiver_users:
                continue
        push_to_timeline(user, post)


@kuyruk.task
def post_to_group(group_id, post):
    group = Group.get(group_id)
    if not group:
        logger.info("Invalid group: %s" % group_id)
        return

    # Get member of the group.
    group_key = helpers.group_key(group_id)
    user_ids = redis_conn.hgetall(group_key)
    if not user_ids:
        logger.info("Group:%s has no users." % group_key)
        return

    logger.info("Sending a post to Group:%s" % group_id)
    for user_id in user_ids:
        user = User.get(user_id)
        if not user:
            logger.info("User:%s does not exist" % user_id)
            continue

        # Push the post to the user's timeline
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


@kuyruk.task
def push_notification(user_ids, message):
    redis_conn = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT
    )

    for user_id in user_ids:
        user = User.get(user_id)
        if not user:
            logger.warning("User: %s could not be found." % user_id)
            continue

        notification = Notification(message=message,
                                    user_id=user_id)
        session.add(notification)
        session.commit()

        try:
            channel = str(user.id) + '_channel'
            message = json.dumps(message)
            redis_conn.publish(channel, message)
        except redis.ConnectionError as err:
            logger.error('Connection error: %s', err)
            # TODO: Handle failed tasks