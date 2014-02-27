import os

RABBIT_HOST = 'localhost'
RABBIT_PORT = 5672
RABBIT_USER = 'guest'
RABBIT_PASSWORD = 'guest'
SAVE_FAILED_TASKS = True
MAX_LOAD = 20

if os.environ.get("CHAPSTREAM_ENV") == "TEST":
    EAGER = True
