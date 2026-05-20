import urllib.request
import json
import ssl
import urllib.error

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'http://127.0.0.1:5000/api/download'
data = json.dumps({'url': 'https://www.youtube.com/watch?v=jNQXAC9IVRw'}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req, context=ctx) as r:
        print("Success:", r.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Error code:", e.code)
    print("Error body:", e.read().decode('utf-8'))
except Exception as e:
    print("Exception:", e)
