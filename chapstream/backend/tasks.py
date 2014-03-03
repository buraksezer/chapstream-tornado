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
from chapstream.backend.db.models.comment import Comment


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

kuyruk = Kuyruk(config.task_queue)


def push_to_timeline(user, post):
    try:
        channel = str(user.id) + '_channel'
        timeline = str(user.id) + '_timeline'
        id_ = str(post["id_"])
        post = json.dumps(post)
        # Push user's timeline the current post
        redis_conn.rpush(timeline, post)
        # Set user-post relation to inspect posts while removing
        post_rid = "post_rid::" + id_
        redis_conn.hset(post_rid, str(user.id), config.POST_SOURCE_DIRECT)
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
    # Generate a Redis timeline post id
    post["id_"] = redis_conn.incr(config.POST_RID_HEAD_KEY)

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

    # Get members of the group.
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
def delete_post_from_timeline(post_rid):
    key = "post_rid::" + post_rid
    user_ids = redis_conn.hgetall(key)
    for user_id in user_ids:
        user_timeline = user_id + "_timeline"
        posts = redis_conn.lrange(user_timeline, 0,
                                  config.TIMELINE_MAX_POST_COUNT)
        logger.info(posts)
        for post in posts:
            post_json = json.loads(post)
            if str(post_json["id_"]) == post_rid:
                if not redis_conn.lrem(user_timeline, post):
                    logger.warning("POST_RID:%s could not be found or removed. User %s",
                                   post_rid, user_id)
                if not redis_conn.hdel(key, user_id):
                    logger.warning("User:%s could not be removed from POST_RID:%s",
                                   user_id, post_rid)

                
@kuyruk.task
def block_user(user_id, chap_id):
    user = User.get(user_id)
    chap = User.get(chap_id)

    if not user or not chap:
        logger.error("Users could not be found: User:%s Blocked:%s" %
                     (user_id, chap_id))
        return

    def remove_posts(timeline, blocked_user):
        posts = redis_conn.lrange(timeline, 0,
                                  config.TIMELINE_MAX_POST_COUNT)
        for post in posts:
            post_json = json.loads(post)
            if post_json["user_id"] == blocked_user.id:
                logger.info("Remove post from: %s. Post: %s"
                            % (blocked_user.name, post))
                if redis_conn.lrem(timeline, post):
                    post_rid = str(post_json["id_"])
                    key = "post_rid::" + post_rid
                    if not redis_conn.hdel(key, str(blocked_user.id)):
                        logger.warning("User:%s could not be removed from POST_RID:%s",
                                       user_id, post_rid)
                else:
                    logger.warning("POST_RID:%s could not be removed or found.",
                                   post_rid)

    # Remove posts from the user who blocks a user.
    user_timeline = str(user.id) + '_timeline'
    remove_posts(user_timeline, chap)

    # Remove posts from the blocked user.
    chap_timeline = str(chap.id) + '_timeline'
    remove_posts(chap_timeline, user)


@kuyruk.task
def push_notification(user_ids, message):
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


@kuyruk.task
def push_comment(comment):
    def push(user_id, rule=None):
        try:
            channel = str(user_id) + '_channel'
            comment["rule"] = rule
            comment_json = json.dumps(comment)
            logger.info('Sending a comment to %s', channel)
            redis_conn.publish(channel, comment_json)
        except redis.ConnectionError as err:
            logger.error('Connection error: %s', err)
            # TODO: Handle failed tasks

    intr_users = Comment.query.with_entities(Comment.user_id).\
        filter_by(post_id=comment["post_id"]).all()
    intr_users = set(intr_users)
    for (user_id,) in intr_users:
        push(user_id, rule=config.REALTIME_COMMENT)

    relations = UserRelation.query.with_entities(UserRelation.user_id).\
        filter_by(chap_id=comment['user_id'],
                  is_banned=False).all()
    for (user_id,) in relations:
        push(user_id)
