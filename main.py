import requests
import json

url = "https://api.binance.com/sapi/v1/capital/deposit/hisrec?timestamp=1656775551286&signature=71ee09f19d348bea59c7bd0adec813f9850283990f4ef9610f2f4ff5dabbc49e"

payload = {}
headers = {
  'Content-Type': 'application/json',
  'X-MBX-APIKEY': '<binance api keyo>'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
