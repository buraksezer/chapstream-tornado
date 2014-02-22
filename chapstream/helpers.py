import gc

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
    return user + "_groups"