import uuid
import logging
import hashlib
import calendar

import tornado
import tornado.web

from chapstream import config
from chapstream.api import decorators
from chapstream.api import CsRequestHandler, process_response
from chapstream.backend.db.models.user import User, UserRelation
from chapstream.backend.db.models.post import Post

logger = logging.getLogger(__name__)


class UserHandler(CsRequestHandler):
    @tornado.web.authenticated
    @decorators.api_response
    def get(self, username):
        user = self.session.query(User).filter_by(name=username).first()
        if not user:
            result = process_response(
                message="%s could not be found." % username,
                status=config.API_ERROR
            )
        else:
            posts = Post.query.filter_by(user_id=user.id)\
                .order_by("id desc")\
                .limit(config.TIMELINE_CHUNK_LENGTH)\
                .all()

            length = len(posts)
            for index in xrange(0, length):
                post = posts[index]
                created_at = calendar.timegm(post.created_at.utctimetuple())
                posts[index] = {
                    "post_id": post.id,
                    "body": post.body,
                    "created_at": created_at
                }

            data = {
                "user": {
                    "name": user.name,
                    "fullname": user.fullname
                },
                "posts": posts,
            }
            result = process_response(data=data, status=config.API_OK)

        return result


class LoginHandler(CsRequestHandler):
    @decorators.not_authenticated
    def get(self):
        self.render("login.html")

    def post(self):
        name = self.get_argument("name")
        password = self.get_argument("password")

        user = self.session.query(User).filter_by(name=name).first()
        if not user:
            # TODO: Use flash messages to handle that
            self.write("Invalid user name.")
            return

        if user.authenticate(password):
            self.set_secure_cookie("user", self.get_argument("name"))
            self.redirect(self.get_argument("next", "/"))
            return

        self.write("Invalid password for %s" % name)


class LogoutHandler(CsRequestHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.write("Goodbye.")
        return


class RegisterHandler(CsRequestHandler):
    @decorators.not_authenticated
    def get(self):
        self.render("register.html")

    def post(self):
        """
        Registers a user
        """
        # TODO: Check validation and None conditions.
        email = self.get_argument("email")
        name = self.get_argument("name")
        password = self.get_argument("password")

        # TODO: We should use flash messages to handle these conditions
        mail_in_use = self.session.query(User).filter_by(email=email).first()
        if mail_in_use:
            self.write("%s is already in use." % email)
            return
        name_taken = self.session.query(User).filter_by(name=name).first()
        if name_taken:
            self.write("%s is already taken by someone else." % name)
            return

        # Register the user
        salt = unicode(uuid.uuid4().hex)
        hash = hashlib.sha512(password + salt).hexdigest()
        new_user = User(name=name, hash=hash, email=email, salt=salt)
        self.session.add(new_user)
        self.session.commit()

        # TODO: Use a seperated page to show after registering for marketing
        self.write("Congurulations!")


class RelationshipStatusHandler(CsRequestHandler):
    @tornado.web.authenticated
    @decorators.api_response
    def get(self, username):
        # TODO: Find a cheap way?
        result = {'rule': None}
        if self.current_user.name == username:
            result["rule"] = "YOU"
            return process_response(data=result, status=config.API_OK)

        chap = self.session.query(User).filter_by(name=username).first()
        if not chap:
            return process_response(data=result, status=config.API_FAIL)

        relation = self.session.query(UserRelation).\
            filter_by(user_id=self.current_user.id,
                      chap_id=chap.id).first()

        if relation:
            result['rule'] = "BANNED" if \
                relation.is_banned else "SUBSCRIBED"

        return process_response(data=result, status=config.API_OK)


class SubscriptionHandler(CsRequestHandler):
    @tornado.web.authenticated
    @decorators.api_response
    def post(self, username):
        chap = self.session.query(User).filter_by(
            name=username).first()
        rel = UserRelation(user_id=self.current_user.id,
                           chap_id=chap.id)
        self.session.add(rel)
        self.session.commit()
        status = config.API_OK if rel.id else config.API_FAIL

        return process_response(status=status)

    @tornado.web.authenticated
    @decorators.api_response
    def delete(self, username):
        chap = self.session.query(User).filter_by(
            name=username).first()
        if not chap:
            return process_response(status=config.API_FAIL,
                                    message="%s could not be found." % username)

        rel = self.session.query(UserRelation).filter_by(
            user_id=self.current_user.id,
            chap_id=chap.id).first()
        if not rel:
            return process_response(status=config.API_FAIL,
                                    message="Relationship could not be found.")
        self.session.delete(rel)
        self.session.commit()

        return process_response(status=config.API_OK)


class BlockHandler(CsRequestHandler):
    @tornado.web.authenticated
    @decorators.api_response
    def post(self, username):
        chap = self.session.query(User).filter_by(
            name=username).first()
        if not chap:
            return process_response(status=config.API_FAIL,
                                    message="%s could not be found." % username)

        rel = self.session.query(UserRelation).filter_by(
            user_id=self.current_user.id,
            chap_id=chap.id).first()

        if not rel:
            rel = UserRelation(user_id=self.current_user.id,
                               chap_id=chap.id, is_banned=True)
            self.session.add(rel)
            self.session.commit()
        else:
            if rel.is_banned:
                return process_response(status=config.API_FAIL,
                                        message="%s is already blocked." % username)
            rel.is_banned = True
            self.session.commit()

        return process_response(status=config.API_OK)

    @tornado.web.authenticated
    @decorators.api_response
    def delete(self, username):
        chap = self.session.query(User).filter_by(
            name=username).first()
        if not chap:
            return process_response(status=config.API_FAIL,
                                    message="%s could not be found." % username)

        rel = self.session.query(UserRelation).filter_by(
            user_id=self.current_user.id,
            chap_id=chap.id).first()
        if not rel:
            return process_response(status=config.API_FAIL,
                                    message="Relationship could not be found.")

        if not rel.is_banned:
            # TODO: Fix english.
            return process_response(status=config.API_FAIL,
                                    message="%s is not blocked." % username)
        self.session.delete(rel)
        self.session.commit()

        return process_response(status=config.API_OK)