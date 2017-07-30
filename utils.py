#!/usr/bin/python3
# -*-coding: utf-8-*-


import os
import base64
import time
import hashlib
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4


class ServerStatus:

    __STATUS = False

    @classmethod
    def set_status(cls, status):
        cls.__STATUS = status

    @classmethod
    def get_status(cls):
        return cls.__STATUS


def get_loop():
    return asyncio.get_event_loop()


def str_uuid():
    return str(uuid4())


def timestamp():
    """
        return a integer of UNIX timestamp in milliseconds
    """
    return int(time.time() * 1000)


def today():
    """
        return an iso datetime
    """
    return datetime.today()


def today_iso():
    """
        return today as iso string
    """

    return today().isoformat()


def iso_to_date(iso):
    """
        get a iso date string and return a datetime object
    """
    return datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S.%fZ")


def get_datetime_plus_delta(minutes=260):
    return datetime.now() + timedelta(minutes=minutes)


def cookie_secret_generator():
    return base64.b64encode(os.urandom(50)).decode('ascii')


def hash_password(password, salt=None):
    salt = salt if salt else cookie_secret_generator()

    passwd_salted = password + salt

    hashed_password = hashlib.sha512(passwd_salted.encode()).hexdigest()
    return hashed_password, salt


def verify_password(password, hashed_password, salt):
    return hash_password(password, salt)[0] == hashed_password


def convert_bdd_datetime(strf, lines):
    def func(line):
        for d in line:
            try:
                yield d.strftime(strf)
            except Exception:
                yield d

    return [list(func(line)) for line in lines]


def format_as_table(head, body):
    return {
        "head": [head],
        "body": body
    }
