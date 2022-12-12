import requests

import binance_bot_get_signed_request
from config import token


def send_line_notify(message):
    # HTTP 標頭參數與資料
    headers = {"Authorization": "Bearer " + token}
    data = {"message": message}

    # 以 requests 發送 POST 請求
    requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)


account_snapshot = binance_bot_get_signed_request.get_account_snapshot()

send_line_notify(account_snapshot)
