import os

# Project settings are defined here.
tornado_settings_template = dict(
    static_path = "static",
    template_path = "templates",
    xsrf_cookies = True,
    autoescape = None,
    session_age = 7 * 24 * 60 * 60,
    cookie_secret = "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    login_url = "/login"
)

if os.environ.get("CHAPSTREAM_ENV") == "TEST":
    # Tornado related settings
    tornado_settings_template["xsrf_cookies"] = False
    tornado_server_settings = tornado_settings_template

    # Database related settings
    POSTGRES_USERNAME = "csdbuser"
    POSTGRES_PASSWORD = "hadron"
    POSTGRES_DATABASE = "csdatabase_test"
    POSTGRES_HOSTNAME = "localhost"
else:
    # Tornado related settings
    tornado_server_settings = tornado_settings_template

    # Database related settings
    POSTGRES_USERNAME = "csdbuser"
    POSTGRES_PASSWORD = "hadron"
    POSTGRES_DATABASE = "csdatabase_test"
    POSTGRES_HOSTNAME = "localhost"


REDIS_KEY_DELIMITER = "::"

TIMELINE_MAX_POST_COUNT = 800
TIMELINE_CHUNK_SIZE = 15

# Start value of the id numbers of timeline posts
POST_RID = 0
POST_RID_HEAD_KEY = "post_rid_head"

POST_SOURCE_DIRECT = "direct"
POST_SOURCE_REPOST = "repost"

# API request status
API_OK = "OK"
API_ERROR = "ERROR"
API_FAIL = "FAIL"

# Redis Configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = None