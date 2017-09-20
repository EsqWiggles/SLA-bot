import asyncio
import json

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

async def read():
    await update()
    latest_alert = cache[0]['text']
    lines = latest_alert.splitlines()
    code_color = 'fix' if len(lines) >= 10 else ''
    header = '-' * len(lines[0])
    lines.insert(1, header)
    text = '\n'.join(lines)
    return '```{}\n{}\n```'.format(code_color, text)