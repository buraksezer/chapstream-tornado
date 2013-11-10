#!/usr/bin/env python

# Import frequently used stdlib modules
import os
import sys
from time import time, sleep
from datetime import date, datetime, timedelta


# Conveniece functions to use in shell
now = lambda: datetime.now()
today = lambda: date.today()


# Import these automatically so they can be used from shell.
from chapstream.backend.db import session, chapstream_engine

# Import all models dynamically
#from chapstream.helpers import find_subclasses
from chapstream.backend.db.models.user import User
#from chapstream.backend.db import Base
#_M = sys.modules[__name__]
#for model in find_subclasses(Base):
#    setattr(_M, model.__name__, model)


# Exit from shell automatically if it is not used
import signal
import threading
from IPython.frontend.terminal.ipapp import load_default_config
from IPython.frontend.terminal.embed import InteractiveShellEmbed

IDLE_SECONDS = 300


def checker():
    shown_warning = False
    while not stop_background_thread.is_set():
        passed = datetime.utcnow() - last_command_time

        if passed.seconds > IDLE_SECONDS - 60 and not shown_warning:
            print "\nShell is inactive and will be closed in a minute " \
                  "if you dont press enter key."
            shown_warning = True

        if passed.seconds > IDLE_SECONDS:
            print "\nShell is not used for %s seconds and " \
                  "exiting... " % IDLE_SECONDS

            ipshell.exit_now = True
            os.kill(os.getpid(), signal.SIGINT)
            return

        sleep(0.1)


def start_background_thread():
    stop_background_thread.clear()
    thread = threading.Thread(target=checker)
    thread.start()


def update_last_command_time(self):
    global last_command_time
    last_command_time = datetime.utcnow()


ipshell = None
last_command_time = None
stop_background_thread = threading.Event()

banner = "   ______ __                    ______   _                                   \n" + \
         " .' ___  [  |                 .' ____ \ / |_                                 \n" + \
         "/ .'   \_|| |--.  ,--. _ .--. | (___ \_`| |-_ .--. .---. ,--.  _ .--..--.    \n" + \
         "| |       | .-. |`'_\ [ '/'`\ \_.____`. | |[ `/'`\/ /__\`'_\ :[ `.-. .-. |   \n" + \
         "\ `.___.'\| | | |// | || \__/ | \____) || |,| |   | \__.// | |,| | | | | |   \n" + \
         " `.____ .[___]|__\'-;__| ;.__/ \______.'\__[___]   '.__.\'-;__[___||__||__]  \n" + \
         "                      [__|                                                   \n"

if __name__ == '__main__':
    # Configure IPython shell
    config = load_default_config()
    ipshell = InteractiveShellEmbed(config=config)
    ipshell.set_hook('pre_prompt_hook', update_last_command_time)

    # Start IPython
    last_command_time = datetime.utcnow()
    threading.Event()
    ipshell(banner)
    stop_background_thread.set()
    print 'Done.'
