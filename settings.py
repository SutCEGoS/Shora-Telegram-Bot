import os

TOKEN = os.environ.get('SHORA_TELEGRAM_KEY', '')
SIGNING_SECRET = os.environ.get('SHORA_SIGN_SECRET', '')
SHORA_CALLBACK_URL = 'http://shora.ce.sharif.edu/issues/ajax/bot/add'
SLEEP_TIME = 10
DSN_ADDRESS = '/home/shora/config/bot_dsn.conf'
