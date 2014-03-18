import gc

from chapstream.config import REDIS_KEY_DELIMITER


def find_subclasses(cls):
    # TODO: Review this function
    all_refs = gc.get_referrers(cls)
    results = []
    for obj in all_refs:
        # __mro__ attributes are tuples
        # and if a tuple is found here, the given class is one of its members
        if (isinstance(obj, tuple) and
            # check if the found tuple is the __mro__ attribute of a class
                getattr(obj[0], "__mro__", None) is obj):
            results.append(obj[0])
    return results


def group_key(group_id):
    return "group_" + str(group_id)


def user_groups_key(user):
    return str(user) + "_groups"


def user_channel(user_id):
    return str(user_id) + REDIS_KEY_DELIMITER + 'channel'


def user_timeline(user_id):
    return str(user_id) + REDIS_KEY_DELIMITER + 'timeline'

def post_rid_key(rid):
    return "post_rid" + REDIS_KEY_DELIMITER + str(rid)


def comment_summary_key(post_id):
    return "cs" + REDIS_KEY_DELIMITER + str(post_id)


def userintr_hash(user_id):
    return "userintr" + REDIS_KEY_DELIMITER + str(user_id)


def userlike_key(user_id):
    return "userlike"+ REDIS_KEY_DELIMITER + str(user_id)


def postlike_key(post_id):
    return "postlike"+ REDIS_KEY_DELIMITER + str(post_id)


