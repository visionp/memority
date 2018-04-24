import os

import raven

from settings import settings

raven_client = raven.Client(
    dsn='https://7f943c9a0edc4af688fab169e0cac527:0c84e4329d044d589763e6c852a14d84@sentry.io/306286',

    # inform the client which parts of code are yours
    # include_paths=['my.app']
    include_paths=[os.path.dirname(__file__)],
    name=f'hoster #{settings.renter_app_port}',
    ignore_exceptions=[
        KeyboardInterrupt,
        NotImplementedError,
        'asyncio.CancelledError'
    ]

    # release=raven.fetch_git_sha(os.path.join(os.path.dirname(__file__), os.pardir)),
)
