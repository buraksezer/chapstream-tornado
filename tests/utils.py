import random

from chapstream.backend.db.models.user import User

RANDINT_MAX = 1000
RANDINT_MIN = 0
USERNAME_TEMPLATE = "user"
DEFAULT_PASSWORD = "hadron"


def create_test_user(username=None):
    if not username:
        username_prefix = random.randint(RANDINT_MIN, RANDINT_MAX)
        username = "_".join([USERNAME_TEMPLATE, username_prefix])

