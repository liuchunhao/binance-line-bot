import hmac
import time
import hashlib
import requests
import json
from urllib.parse import urlencode, quote
import datetime
from datetime import timezone

from io import StringIO
import sys

""" This is a very simple script working on Binance API

- work with USER_DATA endpoint with no third party dependency
- work with testnet

Provide the API key and secret, and it's ready to go

Because USER_DATA endpoints require signature:
- call `send_signed_request` for USER_DATA endpoints
- call `send_public_request` for public endpoints

"""

KEY = "!@#$QWERasdf"
SECRET = "VCZXAQ!@#$"
# BASE_URL = 'https://dapi.binance.com'           # production base url
# BASE_URL = "https://testnet.binancefuture.com"  # testnet base url
# BASE_URL = "https://testnet.binance.vision"     # testnet base url
BASE_URL = 'https://api.binance.com'  # production base url

""" ======  begin of functions, you don't need to touch ====== """


def hashing(query_string):
    return hmac.new(
        SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def get_timestamp():
    return int(time.time() * 1000)


def dispatch_request(http_method):
    session = requests.Session()
    session.headers.update(
        {"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": KEY}
    )
    return {
        "GET": session.get,
        "DELETE": session.delete,
        "PUT": session.put,
        "POST": session.post,
    }.get(http_method, "GET")


def send_signed_request(http_method, url_path, payload={}):
    query_string = urlencode(payload)
    query_string = query_string.replace("%27", "%22")
    if query_string:
        query_string = "{}&timestamp={}".format(query_string, get_timestamp())
    else:
        query_string = "timestamp={}".format(get_timestamp())
    url = (
            BASE_URL + url_path + "?" + query_string + "&signature=" + hashing(query_string)
    )
    print(url)
    params = {"url": url, "params": {}}
    response = dispatch_request(http_method)(**params)
    print(response)
    return response.json()


# used for sending public data request
def send_public_request(url_path, payload={}):
    query_string = urlencode(payload, True)
    url = BASE_URL + url_path
    if query_string:
        url = url + "?" + query_string
    print("{}".format(url))
    response = dispatch_request("GET")(url=url)
    return response.json()


""" ======  end of functions ====== """

### public data endpoint, call send_public_request #####


def get_server_time():
    response = send_public_request("/api/v3/time")
    print(response)


def get_system_status():
    response = send_public_request("/sapi/v1/system/status")
    print(response)


### USER_DATA endpoints, call send_signed_request #####


def get_api_trading_status():
    response = send_signed_request("GET", "/sapi/v1/account/apiTradingStatus")
    print(response)


def get_account_status():
    response = send_signed_request("GET", "/sapi/v1/account/status")
    print(response)


def get_deposit_address():
    params = {
        'coin': 'BNB'
    }
    response = send_signed_request("GET", "/sapi/v1/capital/deposit/address", params)
    print(response)


def get_api_restriction():
    params = {}
    response = send_signed_request("GET", "/sapi/v1/account/apiRestrictions", params)
    print(response)


def trans_unix_time(unix_time):
    timestamp = datetime.datetime.fromtimestamp(unix_time)
    return timestamp.strftime('%Y%m%d %H:%M:%S')


# noinspection SpellCheckingInspection
def get_account_snapshot():
    params = {
        'type': 'FUTURES',
        'limit': 1,
    }
    response = send_signed_request("GET", "/sapi/v1/accountSnapshot", params)
    print(response)
    print('response code: {}'.format(response['code']))
    print()
    last_wallet_balance = '0'

    now = datetime.datetime.today()
    today = datetime.datetime(now.year, now.month, now.day)

    for snapshot in response['snapshotVos']:
        # print(snapshot)
        # print('today: {}'.format(today))

        update_time = int(snapshot['updateTime']) / 1000
        timestamp = datetime.datetime.fromtimestamp(update_time)
        print('dateTime > today: {}'.format(timestamp > today))

        if timestamp > today:
            old_stdout = sys.stdout
            sys.stdout = new_stdout = StringIO()

        timestamp.strftime('%Y%m%d %H:%M:%S')
        print()
        print('更新時間: {}'.format(timestamp))
        data = snapshot['data']
        ast = ''
        wallet_balance = 0
        interest = 0
        assets = data['assets']
        for asset in assets:
            # print(assets)
            ast = asset['asset']
            # margin_balance = round(float(asset['marginBalance']), 2)
            wallet_balance = round(float(asset['walletBalance']), 2)
            interest = round(float(asset['walletBalance']) - float(last_wallet_balance), 2)
            last_wallet_balance = wallet_balance
            # print('保證金餘額: {}'.format(margin_balance))
        positions = data['position']
        total_unrealized_profit = 0
        for position in positions:
            # print(position)
            symbol = position['symbol']
            if symbol in ['BTCUSDT', 'BNBUSDT']:
                entry_px = round(float(position['entryPrice']), 2)
                mark_px = round(float(position['markPrice']), 2)
                amt = round(float(position['positionAmt']), 2)
                unrealized_profit = round((mark_px - entry_px) * amt, 2)
                total_unrealized_profit = round(total_unrealized_profit + unrealized_profit, 2)
                print()
                print('[合約]')
                print('{}|數量: {}'.format(symbol, amt))
                print('成本價: {}'.format(entry_px, mark_px))
                print('市價: {}'.format(mark_px))
                print('未實現損益: {}'.format(unrealized_profit))
        print()
        print('[資金]')
        print('U本位: {}'.format(ast))
        print('利息: {}'.format(interest))
        print('錢包餘額: {}'.format(wallet_balance))
        print('未實現損益(總計): {}'.format(total_unrealized_profit))
        print('總資產: {}'.format(total_unrealized_profit + wallet_balance))

    sys.stdout = old_stdout
    return new_stdout.getvalue()


def output_string():
    old_stdout = sys.stdout
    sys.stdout = new_stdout = StringIO()
    print('Hello')
    print('World')
    sys.stdout = old_stdout
    print('DONE')
    return new_stdout.getvalue()


account_snapshot = get_account_snapshot()
print('account_snapshot:')
print(account_snapshot)

# output = output_string()
# print('output:')
# print('{}'.format(output))
