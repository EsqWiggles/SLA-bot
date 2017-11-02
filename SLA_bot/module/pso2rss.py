import aiohttp
import asyncio
import datetime as dt
import html
import re
import urllib.parse

import SLA_bot.config as cf
import SLA_bot.util as ut

api_key = cf.get('General', 'google_api_key')
api_url = 'https://www.googleapis.com/urlshortener/v1/url?key=' + api_key
cache = ''
common_url = 'http://pso2.jp/players/'
shorten_url = 'https://www.googleapis.com/urlshortener/v1/url'
source_url = 'http://pso2.jp/players/pso2news.xml'
translate_base = 'https://translate.google.com/translate?sl=ja&tl=en&u='
url_cache = {}

async def update():
    async with aiohttp.ClientSession() as session:
        async with session.get(source_url) as response:
            global cache
            cache = await parse(await response.text())

async def parse(xml_text):
    items = re.finditer('<item.*?>.*?</item>', xml_text, re.DOTALL)
    max_items = cf.getint('PSO2 RSS', 'max_items')
    lines= []
    for i, match in enumerate(items):
        if i >= max_items:
            break
        item = match.group()
        link = ut.strip_tags('link', item)
        date = ut.strip_tags('dc:date', item)
        if date:
            date = re.sub('(?<=[+-]..):', '', date )
            date = dt.datetime.strptime(date , '%Y-%m-%dT%H:%M:%S%z')
            date = date.strftime('%m/%d')
        else:
            date = '--/--'
        if link:
            link = html.unescape(link)
            translate = translate_base + urllib.parse.quote_plus(link)
            shortened = await shorten_url(translate)
            link_name = link.replace(common_url, '')
            lines.append('`{}` [{}]({})'.format(date, link_name, shortened))
    return '\n'.join(lines)

async def shorten_url(url):
    global url_cache
    if url in url_cache:
        return url_cache[url]
    if len(url_cache) >= 1000:
        url_cache.clear()
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json={ 'longUrl': url}) as response:
            if response.status == 200:
                short_url = (await response.json())['id']
                url_cache[url] = short_url
                return short_url
            return None

def read():
    if not cache:
        return '`--/--` Not found.'
    return cache[:1024]
