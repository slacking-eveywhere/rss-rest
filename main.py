#!/usr/bin/python3
# -*-coding: utf-8-*-

import tornado.web
from routes import add_route
from server import start_server
from bdd.bdd import query, QueryError, RequestString
from utils import hash_password, today


class Project(tornado.web.RequestHandler):
    async def get(self, _id=None, *args):

        request = RequestString()

        request.add_cond("""
            SELECT id, name, creation_date, modification_date, create_by FROM projects
        """)

        if _id:
            request.add_cond("WHERE id=%s", (_id,))

        sql, params = request.to_string()

        try:
            projects = await list_assets("projects", sql, params, self.format_project)
            self.write(projects)
        except QueryError as e:
            print({'error': e.reason})
        finally:
            self.finish()

    async def post(self, *args):
        name = self.get_argument('name', None)
        user_id = self.get_argument('user_id', None)

        if name and user_id:

            sql = """
                INSERT INTO projects
                (name, creation_date, modification_date, create_by)
                VALUES
                (%s, %s, %s, %s)
            """

            try:
                cursor = await query(sql, (name, today(), today(), user_id))
                self.write({
                    'success': cursor.lastrowid
                })
            except QueryError as e:
                if e.code == 1452:
                    self.write({'error': "user_id not valid"})
                else:
                    self.write({
                        'error': e.reason
                    })

        self.finish()

    async def put(self, _id=None, *args):
        name = self.get_argument("name")

        sql = """
            UPDATE projects SET name=%s, modification_date=%s WHERE id=%s
        """

        if name and _id:
            try:
                cursor = await query(sql, (name, today(), _id))
                self.write({'success': cursor.lastrowid})
            except QueryError as e:
                self.write({'error': e.reason})

            self.finish()

    async def delete(self, _id=None, *args, **kwargs):
        sql = """
            DELETE FROM projects WHERE id=%s
        """

        if _id:
            try:
                cursor = await query(sql, (_id,))
                self.write({'success': cursor.lastrowid})
            except QueryError as e:
                self.write({'error': 'Something wrong'})

    @staticmethod
    def format_project(line):
        _id, name, creation_date, modification_date, create_by = line
        return {
            'id': _id,
            'name': name,
            'creation_date': creation_date.isoformat(),
            'modification_date': modification_date.isoformat(),
            'create_by': create_by
        }


class Users(tornado.web.RequestHandler):
    async def get(self, _id=None, *args):
        sort_by = self.get_argument("sort_by", None)
        asc = self.get_argument("asc", None)

        request = RequestString()
        request.add_cond("""
            SELECT id, name, creation_date, modification_date FROM users
        """)

        if _id:
            request.add_cond("WHERE id=%s", (_id,))

        if sort_by:
            request.add_cond("ORDER BY %s", (sort_by,))

        sql, params = request.to_string()

        try:
            users = await list_assets("users", sql, params, self.format_user)
            self.write(users)
        except QueryError as e:
            self.write({'error': e.reason})
        finally:
            self.finish()

    async def post(self, *args):
        name = self.get_argument('name', None)
        password = self.get_argument('password', None)

        if name and password:

            sql = """
                    INSERT INTO users
                    (active, creation_date, modification_date, name, password, salt)
                    VALUES
                    (%s, %s, %s, %s, %s, %s)
                """

            hashed_password, salt = hash_password(password)
            params = (True, today(), today(), name, hashed_password, salt)

            try:
                cursor = await query(sql, params)
                self.write({
                    'success': cursor.lastrowid
                })
            except QueryError as e:
                self.write({
                    'error': e.reason
                })

        self.finish()

    async def put(self, _id=None, *args):
        name = self.get_argument("name")

        sql = """
            UPDATE users SET name=%s, modification_date=%s WHERE id=%s
        """

        if name and _id:
            try:
                cursor = await query(sql, (name, today(), _id))
                self.write({'success': cursor.lastrowid})
            except QueryError as e:
                self.write({'error': e.reason})

            self.finish()

    async def delete(self, _id=None, *args):
        sql = """
            DELETE FROM users WHERE id=%s
        """

        if _id:
            try:
                cursor = await query(sql, (_id,))
                self.write({'success': cursor.lastrowid})
            except QueryError as e:
                self.write({'error': 'Something wrong'})

    @staticmethod
    def format_user(line):
        _id, name, creation_date, modification_date = line
        return {
            'id': _id,
            'name': name,
            'creation_date': creation_date.isoformat(),
            'modification_date': modification_date.isoformat()
        }


class RssLinks(tornado.web.RequestHandler):

    async def get(self, _id=None, *args, **kwargs):
        request = RequestString()
        request.add_cond("""
        SELECT id, name, link, creation_date, modification_date, project_id FROM rss_links
        """)

        sql, params = request.to_string()
        try:
            rss_links = await list_assets("rss_links", sql, params, self.format_rss_links)
            self.write(rss_links)
        except QueryError as e:
            self.write({'errors': e.reason})
        finally:
            self.finish()

    async def post(self, *args, **kwargs):
        name = self.get_argument("name", None)
        link = self.get_argument("link", None)
        project_id = self.get_argument("project_id", None)

        sql = """
        INSERT INTO rss_links
        (name, link, creation_date, modification_date, project_id)
        VALUES
        (%s, %s, %s, %s, %s)
        """

        params = (name, link, today(), today(), int(project_id))

        try:
            cursor = await query(sql, params)
            self.write({'success': cursor.lastrowid})
        except QueryError as e:
            self.write({'error': e.reason})

    async def put(self, _id=None, *args, **kwargs):
        pass

    async def delete(self, _id=None, *args, **kwargs):
        sql = """
            DELETE FROM rss_links WHERE id=%s
        """

        if _id:
            try:
                cursor = await query(sql, (_id,))
                self.write({'success': cursor.lastrowid})
            except QueryError as e:
                self.write({'error': 'Something wrong'})

    @staticmethod
    def format_rss_links(line):
        _id, name, link, creation_date, modification_date, project_id = line
        return {
            'id': _id,
            'name': name,
            'link': link,
            'creation_date': creation_date.isoformat(),
            'modification_date': modification_date.isoformat(),
            'project_id': project_id
        }


class Folder(tornado.web.RequestHandler):

    async def get(self):
        pass

    async def post(self, *args, **kwargs):
        pass

    async def put(self, *args, **kwargs):
        pass

    async def delete(self, *args, **kwargs):
        pass


class Feeds(tornado.web.RequestHandler):

    async def get(self, rss_link_id=None):
        if rss_link_id:
            request = RequestString()
            request.add_cond("""
            SELECT title, link, summary, published, is_readed, author, hash FROM rss_content WHERE rss_link_id=%s 
            """)

            sql, params = request.to_string()

            try:
                feeds = await list_assets("feeds", sql, (int(rss_link_id),), self.format_feeds)
                self.write(feeds)
            except QueryError as e:
                self.write({'errors': e.reason})
            finally:
                self.finish()

    @staticmethod
    def format_feeds(line):
        title, link, summary, published, read, author, _hash = line
        return {
            'title': title,
            'link': link,
            'summary': summary,
            'published': published.isoformat(),
            'read': read,
            'author': author,
            'hash': _hash
        }

async def list_assets(_type, sql, params, format_func, *args):
    cursor = await query(sql, params)
    result = await cursor.fetchall()
    return {_type: [format_func(line) for line in result]}


add_route(r"/api/v1/project", Project)
add_route(r"/api/v1/project/((?:\d*)?\d+)", Project)
add_route(r"/api/v1/users", Users)
add_route(r"/api/v1/users/((?:\d*)?\d+)", Users)
add_route(r"/api/v1/rss_links", RssLinks)
add_route(r"/api/v1/rss_links/((?:\d*)?\d+)", RssLinks)
add_route(r"/api/v1/rss_links/((?:\d*)?\d+)/feeds", Feeds)

if __name__ == "__main__":
    cookie_secret = "GY213srYTE5EAYBvuDaEdcuhf954y3/cRi/O+WJ1vHLc1lSo7Zdl2ER3zKI5Oen9q/E="
    start_server(cookie_secret=cookie_secret)