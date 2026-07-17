import os
import requests
from dotenv import load_dotenv

from database import SessionLocal
import models

load_dotenv()

STORE = os.getenv('SHOPIFY_STORE_DOMAIN')
TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
API_VERSION = '2025-01'


def fetch_products():
    url = f'https://{STORE}/admin/api/{API_VERSION}/products.json'
    headers = {'X-Shopify-Access-Token': TOKEN}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('products', [])


def sync_products(merchant_id=1):
    db = SessionLocal()
    products = fetch_products()
    count_p, count_v = 0, 0

    for p in products:
        shopify_id = str(p['id'])
        product = db.query(models.Product).filter_by(shopify_id=shopify_id).first()
        if product is None:
            product = models.Product(shopify_id=shopify_id, merchant_id=merchant_id)
            db.add(product)
        product.title = p['title']
        product.description = p.get('body_html', '')
        first_variant = p['variants'][0] if p['variants'] else None
        product.price = float(first_variant['price']) if first_variant else None
        db.flush()  # gives the product an id before we attach variants
        count_p += 1

        for v in p['variants']:
            variant_id = str(v['id'])
            variant = db.query(models.ProductVariant).filter_by(shopify_variant_id=variant_id).first()
            if variant is None:
                variant = models.ProductVariant(shopify_variant_id=variant_id, product_id=product.id)
                db.add(variant)
            variant.title = v['title']
            variant.price = float(v['price'])
            variant.stock = v.get('inventory_quantity', 0)
            count_v += 1

    db.commit()
    db.close()
    print(f'Synced {count_p} products and {count_v} variants.')


if __name__ == '__main__':
    sync_products()
