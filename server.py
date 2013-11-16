import logging

import tornado.options
import tornado.httpserver
import tornado.ioloop

from chapstream.app import Application

# Start ChapStream development server with debug mode.
if __name__ == "__main__":
    tornado.options.parse_command_line()
    logging.info("Starting tornado server on 0.0.0.0:%d" %
                 tornado.options.options.port)
    server = tornado.httpserver.HTTPServer(request_callback=Application(),
                                           xheaders=True)
    server.listen(tornado.options.options.port)
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(io_loop)
    io_loop.start()