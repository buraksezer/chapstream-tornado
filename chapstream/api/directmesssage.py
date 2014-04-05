import calendar
import logging

import tornado.web
from sqlalchemy import or_

from chapstream import config
from chapstream.api import decorators
from chapstream.backend.db.models.user import User
from chapstream.backend.db.models.directmessage import DirectMessage, \
    DirectMessageThread
from chapstream.api import CsRequestHandler, process_response

logger = logging.getLogger(__name__)


class DirectMessageHandler(CsRequestHandler):
    @tornado.web.authenticated
    @decorators.api_response
    def post(self):
        user = self.get_argument("user", None)
        user = self.session.query(User).filter_by(name=user).first()
        if not user:
            return process_response(status=config.API_FAIL,
                                    message="User:%s is invalid" % user)

        subject = self.get_argument("subject", None)
        body = self.get_argument("body", None)
        if not body and not subject:
            return process_response(status=config.API_FAIL,
                                    message="You must give a body or subject.")

        thread = DirectMessageThread(subject=subject,
                                     user=self.current_user, chap=user)
        self.session.add(thread)
        self.session.commit()

        dm = DirectMessage(body=body, thread=thread)
        self.session.add(dm)
        self.session.commit()

        return process_response()

    @tornado.web.authenticated
    @decorators.api_response
    def get(self, thread_id):
        thread = self.session.query(DirectMessageThread).\
            filter_by(id=thread_id).first()
        if not thread:
            return process_response(status=config.API_FAIL,
                                    message="Thread:%s could not be found." % thread_id)

        thread_ = thread.to_dict()
        created_at = calendar.timegm(thread.created_at.utctimetuple())
        thread_["created_at"] = created_at
        messages = []
        for message in thread.messages.all():
            # TODO: Set message sender
            message_ = message.to_dict()
            created_at = calendar.timegm(message.created_at.utctimetuple())
            message_["created_at"] = created_at
            messages.append(message_)

        result = {"thread": thread_, "messages": messages}

        return process_response(data=result)


class DirectMessageThreadsHandler(CsRequestHandler):
    @tornado.web.authenticated
    @decorators.api_response
    def get(self):
        user_id = self.current_user.id
        threads = self.session.query(DirectMessageThread).filter(
            or_(DirectMessageThread.chap_id == user_id,
                DirectMessageThread.chap_id == user_id)
        )

        threads_ = []
        for thread in threads:
            thread_ = thread.to_dict()
            created_at = calendar.timegm(thread.created_at.utctimetuple())
            thread_["created_at"] = created_at
            threads_.append(thread_)

        return process_response(data={"threads": threads_})