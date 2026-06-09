import urllib.request
import json

data = json.dumps({
    "relationship": "妈妈",
    "recipient_name": "妈妈",
    "questions": ["你好吗"],
    "answers": ["很好"]
}).encode()

req = urllib.request.Request(
    'https://web-production-71583a.up.railway.app/api/generate',
    data=data,
    headers={'Content-Type': 'application/json'}
)

try:
    resp = urllib.request.urlopen(req, timeout=120)
    print('SUCCESS:', resp.read().decode())
except urllib.request.HTTPError as e:
    print('ERROR', e.code)
    print(e.read().decode()[:1000])
