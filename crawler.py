#!/usr/bin/python3
# -*-coding: utf-8-*-


import asyncio
from bdd.bdd import query


async def crawl_rss_feed():
    while True:
        sql = """
        SELECT f.link, p.create_by FROM rss_links as f, projects as p WHERE f.project_id == p.id
        """

        cursor = await query(sql, ())
        results = await cursor.fetchall()

        for result in results:
            print(result)

        await asyncio.sleep(60)