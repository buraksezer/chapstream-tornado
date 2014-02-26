import uuid
import random
import hashlib

from chapstream.backend.db.orm import session
from chapstream.backend.db.models.user import User
from chapstream.backend.db.models.group import Group


RANDINT_MAX = 1000
RANDINT_MIN = 0
NAME_TEMPLATE = "lepton"
DEFAULT_PASSWORD = "hadron"
DEFAULT_EMAIL = "lpms@hadronproject.org"


def generate_random_name():
    username_prefix = random.randint(RANDINT_MIN, RANDINT_MAX)
    return "_".join([NAME_TEMPLATE, str(username_prefix)])


def create_test_user(username=None):
    if not username:
        username = generate_random_name()

    # Register the user
    salt = unicode(uuid.uuid4().hex)
    hash = hashlib.sha512(DEFAULT_PASSWORD + salt).hexdigest()
    new_user = User(name=username, hash=hash,
                    email=DEFAULT_EMAIL, salt=salt)
    session.add(new_user)
    session.commit()

    return new_user


def create_test_group(groupname=None):
    if not groupname:
        groupname = generate_random_name()

    group = Group(name=groupname)
    session.add(group)
    session.commit()

    return group
