import logging

import tornadoredis
from kuyruk import Kuyruk

from chapstream.config import task_queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

kuyruk = Kuyruk(task_queue)

@kuyruk.task
def post_timeline(body, channel):
    connection = tornadoredis.Client()
    connection.connect()
    logger.info('Sending a message to %s', channel)
    connection.publish(channel, body)
