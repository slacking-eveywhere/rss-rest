#!/usr/bin/python3
# -*-coding: utf-8-*-


import sys
import os
import time
import asyncio
import tornado.platform.asyncio
import tornado.httpserver
import tornado.ioloop
from tornado.web import Application

from routes import routes
from crawler import crawl_rss_feed
from bdd.bdd import create_tables
from utils import change_locale


class Server(Application):

    def __init__(self, static_path, cookie_secret):

        settings = {
            "cookie_secret": cookie_secret,
            "static_path": static_path,
            "login_url": "/login",
        }
        Application.__init__(self, routes, **settings)


def start_server(address='0.0.0.0', port=8888, static_path=os.path.join(os.path.dirname(__file__), "static"), cookie_secret=None):
    create_tables()

    bla = """
        server listening :
               - address : %s,
               - port    : %s,

        version de python : %s,
        heure de mise en route: %s
    """

    tornado.platform.asyncio.AsyncIOMainLoop().install()

    change_locale()

    application = Server(static_path, cookie_secret)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port, address=address)
    print(bla % (address, str(port), sys.version, time.strftime("%A %d %B %Y %H:%M:%S")))
    loop = asyncio.get_event_loop()

    try:
        loop.create_task(crawl_rss_feed())
        loop.run_forever()
    finally:
        pending = asyncio.Task.all_tasks()
        loop.run_until_complete(asyncio.gather(*pending))
        loop.stop()
        loop.close()


if __name__ == "__main__":
    cookie_secret = "GY213srYTE5EAYBvuDaEdcuhf954y3/cRi/O+WJ1vHLc1lSo7Zdl2ER3zKI5Oen9q/E="
    start_server(cookie_secret=cookie_secret)