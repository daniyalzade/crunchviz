#!/usr/bin/python
import os
import tornado.httpserver
import tornado.httpclient
import tornado.web
from tornado.options import define
from tornado.options import parse_command_line
from tornado.options import options

import tornado.ioloop
import tornado.web
import logging
import sys

from handler import CompanyHandler
from handler import StatsHandler
from loggingutils import basicConfig

def main():
    define("port", default="2111", type=int)
    define("debug", default=False, type=bool)
    define("console", default=False, type=bool)
    define("loglevel")
    define("mongo_host", default='localhost')

    parse_command_line()
    basicConfig(options=options)

    # Setup tornado
    handlers = [
                (r'/companies.*?', CompanyHandler,
                    {
                     'mongo_host': options.mongo_host,
                    }
                ),
                (r'/stats.*?', StatsHandler,
                    {
                     'mongo_host': options.mongo_host,
                    }
                ),
                ]
    app_settings = {
            'debug' : options.debug,
            'static_path': os.path.join(os.path.dirname(__file__), "static"),
            'gzip': True
            }
    application = tornado.web.Application(handlers, **app_settings)

    http_server = tornado.httpserver.HTTPServer(application)
    logging.info('traffic_server listening on port %s' % options.port)
    http_server.listen(int(options.port))
    tornado.ioloop.IOLoop.instance().start()

    return 0

if __name__ == "__main__":
    sys.exit(main())

