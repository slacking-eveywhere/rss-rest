#!/usr/bin/python3
# -*-coding: utf-8-*-


import asyncio
from dateutil import parser
import feedparser
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.platform.asyncio import to_asyncio_future
from utils import today, sha_256
from bdd.bdd import query, QueryError


async def fetch_url(url):
    http_client = AsyncHTTPClient()
    page = await http_client.fetch(url)
    return page.body


async def insert_feed_article(entries, rss_link_id):

    for entry in entries:
        summary = entry.get('summary', '')
        published = entry.get('published', None)
        if published:
            published = parser.parse(published)
        else:
            published = today()

        params = (
            entry.get('link', ''),
            entry.get('title', ''),
            summary,
            published,
            entry.get('author', ''),
            sha_256(summary),
            rss_link_id
        )

        insert_sql = """
        INSERT INTO rss_content 
        (link, title, summary, published, author, hash, rss_link_id)
        VALUES
        (%s, %s, %s, %s, %s, %s, %s)
        """

        try:
            insert_cursor = await query(insert_sql, params)
            print(insert_cursor.lastrowid)
        except QueryError as e:
            if e.code == 1062:
                pass
            else:
                print(e)


async def crawl_rss_feed():
    sql = """
    SELECT f.id, f.link, p.create_by FROM rss_links as f, projects as p WHERE f.project_id = p.id
    """
    while True:
        try:
            cursor = await query(sql, ())
            results = await cursor.fetchall()
        except QueryError:
            print(e)
        else:
            for _id, link, user_id in results:
                try:
                    result = await to_asyncio_future(fetch_url(link))
                    rss = feedparser.parse(result)
                    entries = rss.get("entries", [])
                    await insert_feed_article(entries, _id)
                except HTTPError as e:
                    print(link, e)

        await asyncio.sleep(60)