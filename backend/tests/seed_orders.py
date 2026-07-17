import os, hmac, hashlib, base64, json, requests, time
from dotenv import load_dotenv

load_dotenv()
SECRET = os.getenv('SHOPIFY_WEBHOOK_SECRET', '')
URL = 'http://127.0.0.1:8000/webhooks/order'

# Simulate purchases (not every checkout converts - realistic drop-off).
orders = ['49.99', '24.99', '59.99', '79.99', '24.99']

for total in orders:
    body = json.dumps({'total_price': total, 'note_attributes': [{'name': 'conversation_id', 'value': '1'}]}).encode('utf-8')
    sig = base64.b64encode(hmac.new(SECRET.encode(), body, hashlib.sha256).digest()).decode()
    r = requests.post(URL, data=body, headers={'Content-Type': 'application/json', 'X-Shopify-Hmac-Sha256': sig})
    print('order', total, '->', r.json())
    time.sleep(0.3)

print('Done.')
