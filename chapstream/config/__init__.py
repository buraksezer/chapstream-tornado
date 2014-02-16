# Project settings are defined here.

tornado_server_settings = dict(
    static_path = "static",
    template_path = "templates",
    xsrf_cookies = True,
    autoescape = None,
    session_age = 7 * 24 * 60 * 60,
    cookie_secret = "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    login_url = "/login"
)

TIMELINE_CHUNK_SIZE = 15

# API request status
API_OK = "OK"
API_ERROR = "ERROR"
API_FAIL = "FAIL"

# Redis Configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = None