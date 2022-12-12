from binance.websocket.spot.websocket_client import SpotWebsocketClient as WebsocketClient
import config

import time
import logging
from binance.lib.utils import config_logging


config_logging(logging, logging.DEBUG)

def message_handler(message):
    print(message)

ws_client = WebsocketClient()
ws_client.start()

ws_client.mini_ticker(
    symbol='bnbusdt',
    id=1,
    callback=message_handler,
)

# Combine selected streams
ws_client.instant_subscribe(
    stream=['bnbusdt@bookTicker', 'ethusdt@bookTicker'],
    callback=message_handler,
)

# ws_client.stop()
