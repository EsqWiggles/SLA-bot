import aiohttp
import asyncio
import html
import re

import SLA_bot.config as cf
import SLA_bot.util as ut

cache = ''
source_url = 'http://www.bumped.org/psublog/feed/'

async def update():
    async with aiohttp.ClientSession() as session:
        async with session.get(source_url) as response:
            global cache
            cache = await parse(await response.text())

async def parse(xml_text):
    items = re.finditer('<item.*?>.*?</item>', xml_text, re.DOTALL)
    max_items = cf.getint('bumped RSS', 'max_items')
    lines= []
    for i, match in enumerate(items):
        if i >= max_items:
            break
        item = match.group()
        title = ut.strip_tags('title', item)
        link = ut.strip_tags('link', item)
        date = ut.strip_tags('pubDate', item)
        if date:
            date = re.sub(r'^..., (\d\d) (\D\D\D).*', r'\2 \1', date)
        else:
            date = '--- --'
        if link:
            link = html.unescape(link)
            if title:
                lines.append('`{}` [{}]({})'.format(date, title, link))
            else:
                lines.append('`{}` {}'.format(date, link))
    return '\n'.join(lines)

def read():
    if not cache:
        return '`--/--` Not found.'
    return (cache + '\n** **')[:1024]