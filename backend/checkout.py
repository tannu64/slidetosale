import os
import requests
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv('SHOPIFY_STORE_DOMAIN')
TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
API_VERSION = '2025-01'


def create_checkout_link(shopify_variant_id, quantity=1):
    url = f'https://{STORE}/admin/api/{API_VERSION}/draft_orders.json'
    headers = {
        'X-Shopify-Access-Token': TOKEN,
        'Content-Type': 'application/json',
    }
    payload = {
        'draft_order': {
            'line_items': [
                {
                    'variant_id': int(shopify_variant_id),
                    'quantity': quantity,
                }
            ]
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    draft = response.json()['draft_order']
    return draft.get('invoice_url')
