#!/usr/bin/python3
# -*-coding: utf-8-*-


import asyncio
import pymysql
from aiomysql import connect, create_pool, cursors


CREDS = {
    "host": '192.168.1.20',
    "port": 3306,
    "user": 'rss_feed_user',
    "password": 'rss_feed',
    "db": 'rss_feed',
    "charset": 'utf8'
}

class Tables:
    __tables = []

    @classmethod
    def add(cls, table):
        cls.__tables.append(table)
        return cls

    @classmethod
    def get(cls):
        return cls.__tables


class Table:
    def __init__(self, name, sql):
        self.name = name
        self.sql = sql


class RequestString:

    def __init__(self):
        self.__sql = []
        self.__params = ()

    def add_cond(self, cond, params=()):
        self.__sql.append(cond)
        if params:
            self.__params = self.__params + params
        return self

    def to_string(self):
        return (' '.join(self.__sql), self.__params)


class QueryError(Exception):
    def __init__(self, excpt):
        code, *reason = excpt.args
        self.code = code
        self.reason = reason


def connection():
    try:
        return pymysql.connect(**CREDS)
    except pymysql.err.OperationalError as e:
        print(e)
        return None


def create_tables():
    conn = connection()
    if conn:
        for table in Tables.get():
            try:
                create_table(conn, table)
            except Exception as e:
                _, reason = e.args
                print(reason)
            else:
                print("Database {} created".format(table.name))
        conn.close()


def create_table(conn, table):
    with conn.cursor() as cursor:
        cursor.execute(table.sql)
        conn.commit()


async def get_conn():
    CREDS['loop'] = asyncio.get_event_loop()
    return await connect(**CREDS)


async def query(sql, params=(), as_dic=False):
    conn = await get_conn()
    cursor_type = cursors.Cursor if as_dic is False else cursors.DictCursor

    try:
        async with conn.cursor(cursor_type) as cur:
            await cur.execute(sql, params)

    except pymysql.err.IntegrityError as e:
        raise QueryError(e)
    except Exception as e:
        raise QueryError(e)
    else:
        if cur.lastrowid is not None:
            await conn.commit()
        return cur
    finally:
        conn.close()


def add_cond(sql, cond, old_params, add_params):
    return ("{} {}".format(sql, cond), old_params + add_params)


def filter_by_id(sql, id):
    pass




Tables.add(
    Table("users", """
        CREATE TABLE users (
        `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `active` BOOLEAN NOT NULL,
        `creation_date` DATETIME NOT NULL,
        `modification_date` DATETIME NOT NULL,
        `name` VARCHAR(255) COLLATE utf8_bin NOT NULL,
        `password` CHAR(128) COLLATE utf8_bin NOT NULL,
        `salt` CHAR(68) COLLATE utf8_bin NOT NULL,
        CONSTRAINT `unique_name`
            UNIQUE(name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1;
    """)).add(
    Table("user_ticket", """
        CREATE TABLE user_ticket (
        `uuid` CHAR(36) NOT NULL,
        `name` VARCHAR(255) NOT NULL,
        `creation_date` DATETIME NOT NULL,
        `revoke_date` DATETIME NOT NULL,
        `socket` CHAR(36)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1;
    """)).add(
    Table("projects", """
        CREATE TABLE projects (
        `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `name` VARCHAR(255) NOT NULL,
        `creation_date` DATETIME NOT NULL,
        `modification_date` DATETIME NOT NULL,
        `create_by` INT NOT NULL,
        CONSTRAINT `project_unique_name`
            UNIQUE(name),
        CONSTRAINT `fk_user_id`
            FOREIGN KEY (create_by) REFERENCES users (id)
            ON UPDATE RESTRICT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1;
    """)).add(
    Table("rss_links", """
    CREATE TABLE rss_links (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255),
    `link` VARCHAR(1024),
    `creation_date` DATETIME NOT NULL,
    `modification_date` DATETIME NOT NULL,
    `project_id` INT NOT NULL,
    CONSTRAINT `fk_project_id`
        FOREIGN KEY (project_id) REFERENCES projects (id)
        ON UPDATE RESTRICT
        ON DELETE CASCADE,
    CONSTRAINT `fk_folder_id`
        FOREIGN KEY (folder_id) REFERENCES folders (id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1;
    """)).add(
    Table("folders", """
    CREATE TABLE folders (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1;
    """)).add(
    Table("rss_content", """
    CREATE TABLE rss_content (
    `link` VARCHAR(1024),
    `title` VARCHAR(255),
    `summary` MEDIUMTEXT,
    `published` DATETIME,
    `is_readed` BOOLEAN DEFAULT FALSE,
    `author` VARCHAR(255),
    `hash` CHAR(64),
    `rss_link_id` INT,
    CONSTRAINT `fk_rss_link`
        FOREIGN KEY (rss_link_id) REFERENCES rss_links (id)
        ON UPDATE RESTRICT
        ON DELETE CASCADE,
    CONSTRAINT `hash_published_unique`
        UNIQUE(published, hash)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1;
    """)
)