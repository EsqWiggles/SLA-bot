import asyncio
import json

import aiohttp

import SLA_bot.config as cf

source_url = 'http://pso2emq.flyergo.eu/api/v2/'

async def download(url):
    try:
        async with aiohttp.get(url) as response:
            return await response.json()
    except json.decoder.JSONDecodeError:
        pass

def parse_data(data):
    latest_alert = data[0]['text']
    lines = latest_alert.splitlines()
    code_color = 'fix' if len(lines) >= 10 else ''
    header = '-' * len(lines[0])
    lines.insert(1, header)
    text = '\n'.join(lines)
    return '```{}\n{}\n```'.format(code_color, text)
        
async def fetch():
    header = cf.get('PSO2 Feed', 'header')
    raw_data = await download(source_url)
    return '** **\n' + header + '\n' + parse_data(raw_data)
