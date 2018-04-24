import asyncio
from collections import namedtuple
from concurrent.futures import FIRST_COMPLETED

import aiohttp

Service = namedtuple('Service', ('name', 'url', 'ip_attr'))

SERVICES = (
    Service('ipify', 'https://api.ipify.org?format=json', 'ip'),
    Service('ip-api', 'http://ip-api.com/json', 'query')
)


async def fetch_ip(service):
    async with aiohttp.ClientSession() as session:
        async with session.get(service.url) as response:
            json_response = await response.json()
            ip = json_response[service.ip_attr]

    return ip


async def get_ip():
    futures = [fetch_ip(service) for service in SERVICES]
    done, pending = await asyncio.wait(
        futures,
        return_when=FIRST_COMPLETED
    )

    for future in pending:
        future.cancel()

    return done.pop().result()


if __name__ == '__main__':
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(get_ip())
    ioloop.close()
