import functools
from urllib2 import HTTPError

def not_authenticated(method):
    """
    Redirect the request to path if not authenticated
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            return method(self, *args, **kwargs)
        if self.request.method in ("GET", "HEAD"):
            self.redirect("/")
            return
        raise HTTPError(403)

    return wrapper