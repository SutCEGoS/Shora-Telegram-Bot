import os
from raven.handlers.logging import SentryHandler
from raven import Client
from raven.conf import setup_logging


TOKEN = os.environ.get('SHORA_TELEGRAM_KEY', '')
SIGNING_SECRET = os.environ.get('SHORA_SIGN_SECRET', '')
SHORA_CALLBACK_URL = 'http://shora.ce.sharif.edu/issues/ajax/bot/add'
SLEEP_TIME = 10

if not TOKEN or not SIGNING_SECRET:
   raise ValueError('Couldn\'t load environment variables')

DSN_ADDRESS = '/home/shora/config/bot_dsn.conf'

setup_logging(SentryHandler(Client(open(DSN_ADDRESS).read().replace('\n', ''))))

