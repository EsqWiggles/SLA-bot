import asyncio
import json

import aiohttp

class AlertFeed:
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
        header = '-' * len(lines[0])
        lines.insert(1, header)
        text = '\n'.join(lines)
        return '```fix\n{}\n```'.format(text)
            
    async def fetch():
        raw_data = await AlertFeed.download(AlertFeed.source_url)
        return AlertFeed.parse_data(raw_data)
