import uuid
import hashlib

import tornado
import tornado.web

from chapstream.api import decorators
from chapstream.api import CsRequestHandler
from chapstream.backend.db import session
from chapstream.backend.db.models.user import User



class ProfileHandler(CsRequestHandler):
    @tornado.web.authenticated
    def get(self):
        self.write("This is your profile")


class LoginHandler(CsRequestHandler):
    @decorators.not_authenticated
    def get(self):
        self.render("login.html")

    def post(self):
        name = self.get_argument("name")
        password = self.get_argument("password")

        user = session.query(User).filter_by(name=name).first()
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
        mail_in_use = session.query(User).filter_by(email=email).first()
        if mail_in_use:
            self.write("%s is already in use." % email)
            return
        name_taken = session.query(User).filter_by(name=name).first()
        if name_taken:
            self.write("%s is already taken by someone else." % name)
            return

        # Register the user
        salt = unicode(uuid.uuid4().hex)
        hash = hashlib.sha512(password + salt).hexdigest()
        new_user = User(name=name, hash=hash, email=email, salt=salt)
        session.add(new_user)
        session.commit()

        # TODO: Use a seperated page to show after registering for marketing
        self.write("Congurulations!")
