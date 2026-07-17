from database import SessionLocal
from ai import generate_response
from search import search_products
from checkout import create_checkout_link
import models


def handle_message(customer_message):
    ai_result = generate_response(customer_message)
    reply = ai_result['reply']
    intent = ai_result['intent']
    product = ai_result.get('product', '')
    variant = ai_result.get('variant', '')

    checkout_link = None

    # Only try to build a link when intent is high AND a specific variant was named.
    if intent == 'high' and product and variant:
        db = SessionLocal()
        matches = search_products(db, product, variant)

        if matches:
            # Find the actual variant row to get its Shopify id.
            found = None
            for p in db.query(models.Product).filter(models.Product.title.ilike(f'%{product}%')).all():
                for v in p.variants:
                    if variant.strip().lower() in (v.title or '').lower():
                        found = v
                        break
                if found:
                    break

            if found and found.stock > 0:
                checkout_link = create_checkout_link(found.shopify_variant_id)
                reply = f'{reply}\n\nHere is your checkout link: {checkout_link}'

        db.close()

    return {
        'reply': reply,
        'intent': intent,
        'checkout_link': checkout_link,
    }
