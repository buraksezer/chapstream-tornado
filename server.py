import tornado.ioloop
from chapstream.app import application

# Start ChapStream development server with debug mode.
if __name__ == "__main__":
    application.listen(8888)
    print("\nChapStream server is running at http://0.0.0.0:8888")
    print("Quit the app with Ctrl+C\n")
    tornado.ioloop.IOLoop.instance().start()
