# Project settings are defined here.

settings = dict(
    static_path = "static",
    template_path = "templates",
    xsrf_cookies = True,
    autoescape = None,
    session_age = 7 * 24 * 60 * 60,
    cookie_secret = "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    login_url = "/login"
)