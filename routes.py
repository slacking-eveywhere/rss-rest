#!/usr/bin/python3
# -*-coding: utf-8-*-


import os
from tornado import web


routes = []


def search_route_by_url(url_to_search):
    for route in routes:
        url, cls, *path = route
        if url_to_search == url:
            return route


def add_route(url, cls, path={}):
    routes.append((url, cls, path))


def add_static_route(url, path_file):
    path = os.path.join(os.getcwd(), "static", path_file)

    routes.append((
        url, web.StaticFileHandler, {"path": path}
    ))


def delete(url):
    route = search_route_by_url(url)
    try:
        routes.remove(route)
    except IndexError:
        print("No route found to delete")