import json
import logging

import redis
from kuyruk import Kuyruk
from sqlalchemy import and_

from chapstream.backend.db import session
from chapstream.backend.db.models.user import User, UserRelation
from chapstream.backend.db.models.group import Group
from chapstream.backend.db.models.post import Post
from chapstream.backend.db.models.notification import Notification
from chapstream.backend.db.models.comment import Comment
from chapstream import config
from chapstream.redisconn import redis_conn
from chapstream.config import task_queue
from chapstream import helpers


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

kuyruk = Kuyruk(config.task_queue)


def push_to_timeline(user, post):
    try:
        channel = helpers.user_channel(user.id)
        timeline = helpers.user_timeline(user.id)
        rid = str(post["rid"])
        post["type"] = config.REALTIME_POST
        post = json.dumps(post)
        # Push user's timeline the current post
        redis_conn.rpush(timeline, post)
        # Set user-post relation to inspect posts while removing
        post_rid = helpers.post_rid_key(rid)
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
    post["rid"] = redis_conn.incr(config.POST_RID_HEAD_KEY)

    # If the owner sends a post to a group, he is already member of the group
    # pushing is not necessary in that case.
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
        if receiver_groups:
            # If the user is a member of the receiver groups,
            # dont send the post to the user.
            for group_id in receiver_groups:
                user_key = str(relation.user_id)
                if redis_conn.sismember(user_key, group_id):
                    group_receiver = True
                    break

            if group_receiver:
                continue

        # if receiver_users is not None, we must send a realtime message to the user
        # about the post
        if receiver_users and not relation.user.name in receiver_users:
            continue
        push_to_timeline(relation.user, post)


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
    key = helpers.post_rid_key(post_rid)
    user_ids = redis_conn.hgetall(key)
    for user_id in user_ids:
        user_timeline = helpers.user_timeline(user_id)
        posts = redis_conn.lrange(user_timeline, 0,
                                  config.TIMELINE_MAX_POST_COUNT)
        for post in posts:
            post_json = json.loads(post)
            if str(post_json["rid"]) == post_rid:
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
                post_rid = str(post_json["rid"])
                if redis_conn.lrem(timeline, post):
                    key = helpers.post_rid_key(post_rid)
                    if not redis_conn.hdel(key, str(blocked_user.id)):
                        logger.warning("User:%s could not be removed from POST_RID:%s",
                                       user_id, post_rid)
                else:
                    logger.warning("POST_RID:%s could not be removed or found.",
                                   post_rid)

    # Remove posts from the user who blocks a user.
    user_timeline = helpers.user_timeline(user.id)
    remove_posts(user_timeline, chap)

    # Remove posts from the blocked user.
    chap_timeline = helpers.user_timeline(user.id)
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

    for user_id in user_ids:
        try:
            channel = helpers.user_channel(user_id)
            message = json.dumps(message)
            redis_conn.publish(channel, message)
        except redis.ConnectionError as err:
            logger.error('Connection error: %s', err)
            # TODO: Handle failed tasks


@kuyruk.task
def push_comment(comment, u_id):
    intr_users = Comment.query.with_entities(Comment.user_id).filter(
        and_(Comment.post_id == comment["post_id"],
             Comment.user_id != u_id)
    ).all()
    relations = UserRelation.query.with_entities(UserRelation.user_id).\
        filter_by(chap_id=u_id,
                  is_banned=False).all()

    user_ids = intr_users + relations
    user_ids = set(user_ids)
    for (user_id,) in user_ids:
        try:
            channel = helpers.user_channel(user_id)
            comment["type"] = config.REALTIME_COMMENT
            comment_json = json.dumps(comment)
            logger.info('Sending a comment to %s', channel)
            redis_conn.publish(channel, comment_json)
        except redis.ConnectionError as err:
            logger.error('Connection error: %s', err)
            # TODO: Handle failed tasks


@kuyruk.task
def push_like(post_id, user_like_id):
    post = Post.get(post_id)
    liked = User.get(user_like_id)
    postlike_key = helpers.postlike_key(post_id)
    length = redis_conn.llen(postlike_key)

    # Includes user names
    usernames_liked = redis_conn.lrange(postlike_key, 0, length)
    logger.info(usernames_liked)
    users_liked = User.query.with_entities(User.id, User.name, User.fullname).\
        filter(User.name.in_(usernames_liked)).all()

    chaps = User.query.with_entities(User.id, User.name, User.fullname).\
        join(UserRelation.chap).\
        filter(and_(UserRelation.user_id == post.user_id,
                    User.name.notin_(usernames_liked))).all()

    owner = (post.user.id, post.user.name, post.user.fullname)
    screen_name = liked.fullname if liked.fullname else liked.name
    data = {
        "type": config.REALTIME_LIKE,
        "post_id": post_id,
        "name": liked.name,
        "screen_name": screen_name
    }

    user_ids = users_liked + chaps + [owner]
    logger.info(user_ids)
    for (user_id, user_name, user_fullname) in set(user_ids):
        if user_id == user_like_id:
            continue
        channel = helpers.user_channel(user_id)
        try:
            data_json = json.dumps(data)
            redis_conn.publish(channel, data_json)
        except redis.ConnectionError as err:
            logger.error('Connection error: %s', err)
            # TODO: Handle failed tasks