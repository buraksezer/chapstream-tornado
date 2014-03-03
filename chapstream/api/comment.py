import json
import logging
import calendar

import tornado.web

from chapstream import config
from chapstream.api import decorators
from chapstream.api import CsRequestHandler, process_response
from chapstream.backend.db.models.post import Post
from chapstream.backend.db.models.comment import Comment
from chapstream.backend.db.models.user import UserRelation
from chapstream.backend.tasks import push_comment

logger = logging.getLogger(__name__)


class CommentHandler(CsRequestHandler):
    @tornado.web.authenticated
    @decorators.api_response
    def post(self, post_id):
        post = self.session.query(Post).filter_by(
            id=post_id).first()
        if not post:
            return process_response(status=config.API_FAIL,
                                    message="Post:%s could not be found."
                                            % post_id)

        logger.info('Creating a new comment by %s',
                    self.current_user.name)

        # Create a database record for this comment on
        # PostgreSQL database
        data = json.loads(self.request.body)
        body = data["body"].decode('UTF-8')
        new_comment = Comment(
            body=body,
            post=post,
            user=self.current_user
        )
        self.session.add(new_comment)
        self.session.commit()

        created_at = calendar.timegm(new_comment.created_at.utctimetuple())
        comment = {
            'type': config.REALTIME_COMMENT,
            'post_id': post.id,
            'id': new_comment.id,
            'body': body,
            'created_at': created_at,
            'user_id': self.current_user.id,
            'name': self.current_user.name,
            'fullname': self.current_user.fullname
        }

        # Comment summary is a list on Redis that stores
        # first two comments and last one to render the user timeline
        # as fast as possible.
        comment_summary = "cs::" + str(post.id)
        length = self.redis_conn.llen(comment_summary)
        comment_json = json.dumps(comment)
        if length in (0, 1):
            self.redis_conn.rpush(comment_summary, comment_json)
        else:
            if length >= 3:
                while length > 2:
                    if self.redis_conn.rpop(comment_summary):
                        length -= 1
            self.redis_conn.rpush(comment_summary, comment_json)

        # TODO: make a helper func. for this
        if post.user_id != self.current_user.id:
            userintr_hash = "userintr:" + str(self.current_user.id)
            val = config.REALTIME_COMMENT+str(created_at)
            self.redis_conn.hset(userintr_hash, str(post.id), val)
            #rel = self.session.query(UserRelation).filter_by(
            #    user_id=self.current_user.id, chap_id=post.id).first()
            #if not rel:
            #    intr_hash = "intr:" + str(post.id)
            #    self.redis_conn.hset(intr_hash,
            #                         str(self.current_user.id),
            #                         config.REALTIME_COMMENT)

        # Send a task for realtime interaction
        push_comment(comment)
        data = {'comment': comment}
        return process_response(data=data)

    @tornado.web.authenticated
    @decorators.api_response
    def get(self, post_id):
        post = self.session.query(Post).filter_by(
            id=post_id).first()
        if not post:
            return process_response(status=config.API_FAIL,
                                    message="Post:%s could not be found."
                                            % post_id)
        result = []
        for comment in post.comments:
            created_at = calendar.timegm(comment.created_at.utctimetuple())
            comment_dict = {
                'id': comment.id,
                'body': comment.body,
                'created_at': created_at,
                'user_id': comment.user.id,
                'name': comment.user.name,
                'fullname': comment.user.fullname
            }
            result.append(comment_dict)

        return process_response(data={"comments": result})

    @tornado.web.authenticated
    @decorators.api_response
    def delete(self, comment_id):
        comment = self.session.query(Comment).filter_by(
            id=comment_id).first()
        if not comment:
            return process_response(status=config.API_FAIL,
                                    message="Comment:%s could not be found."
                                            % comment_id)

        post_id = comment.post.id
        comment_summary = "cs::" + str(post_id)
        items = self.redis_conn.lrange(comment_summary, 0, 3)
        for item in items:
            comment_json = json.loads(item)
            if comment_json["id"] == comment.id:
                self.redis_conn.lrem(comment_summary, item)

        self.session.delete(comment)
        self.session.commit()

        other_comments = self.session.query(Comment).filter_by(
            user_id=self.current_user.id,
            post_id=post_id
        ).count()

        if not other_comments:
            userintr_hash = "userintr:" + str(self.current_user.id)
            self.redis_conn.hdel(userintr_hash, str(post_id))

