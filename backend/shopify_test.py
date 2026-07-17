import os
import requests
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv('SHOPIFY_STORE_DOMAIN')
TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
API_VERSION = '2025-01'

url = f'https://{STORE}/admin/api/{API_VERSION}/products.json'
headers = {'X-Shopify-Access-Token': TOKEN}

response = requests.get(url, headers=headers)
print('Status code:', response.status_code)

data = response.json()
products = data.get('products', [])
print(f'Found {len(products)} products:')
for p in products:
    print('-', p['title'], '| variants:', len(p['variants']))
