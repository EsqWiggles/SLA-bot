import asyncio
import json
import re

import aiohttp

cache = ''
source_url = 'http://pso2emq.flyergo.eu/api/v2/'

async def update():
    try:
        async with aiohttp.get(source_url) as response:
            global cache
            cache = await response.json()
    except json.decoder.JSONDecodeError:
        pass

def align_shiplabels(text):
    def monospace(matched):
        return '`{}`'.format(matched.group(0))
    return re.sub('^\d\d:(?!\d\d\s)', monospace, text, flags=re.MULTILINE)
        
async def read():
    await update()
    latest_alert = cache[0]['text']
    if latest_alert.count('\n') >= 10:
        return align_shiplabels(latest_alert) + '\n** **'
    return latest_alert + '\n** **'
