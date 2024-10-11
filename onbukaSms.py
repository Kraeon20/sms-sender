import os
import hashlib
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()
base_url = os.getenv("onbukaAPIroute")
api_key = os.getenv("onbukaAPIkey")
api_pwd = os.getenv("onbukaAPIpassword")
appid = os.getenv("onbukaAPIappID")

def create_headers():
  timestamp = int(time.time())
  s = "%s%s%s" % (api_key, api_pwd, str(timestamp))
  sign = hashlib.md5(s.encode(encoding='UTF-8')).hexdigest()

  headers = {
    'Content-Type': 'application/json;charset=utf-8',
    'Sign': sign,
    'Timestamp': str(timestamp),
    'Api-Key': api_key
  }

  return headers

headers = create_headers()

url = "%s/sendSms" % base_url
print(url)


body = {"appId": appid, 
        "numbers": "+15099062933", 
        "content": "hello world", 
        "senderId": "123", 
        "orderId": ""}

rsp = requests.post(url, json=body, headers=headers)

if rsp.status_code == 200:
  res = json.loads(rsp.text)
  print(res)