import os
import hmac
import hashlib
import base64
import json
import requests
from dotenv import load_dotenv

load_dotenv()
SECRET = os.getenv('SHOPIFY_WEBHOOK_SECRET', '')
URL = 'http://127.0.0.1:8000/webhooks/order'

# A fake order body, like Shopify would send.
order = {
    'total_price': '49.99',
    'note_attributes': [
        {'name': 'conversation_id', 'value': '1'}
    ],
}
body = json.dumps(order).encode('utf-8')

# Sign it exactly the way Shopify signs webhooks.
digest = hmac.new(SECRET.encode('utf-8'), body, hashlib.sha256).digest()
signature = base64.b64encode(digest).decode('utf-8')

headers = {
    'Content-Type': 'application/json',
    'X-Shopify-Hmac-Sha256': signature,
}

response = requests.post(URL, data=body, headers=headers)
print('Status:', response.status_code)
print('Response:', response.text)
