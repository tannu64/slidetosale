import os
from dotenv import load_dotenv
from groq import Groq

from database import SessionLocal
import models

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL = 'llama-3.3-70b-versatile'

BRAND_TONE = 'friendly and casual, like a helpful person running an Instagram fashion store'


def get_product_context(db):
    lines = []
    products = db.query(models.Product).all()
    for p in products:
        variant_bits = []
        for v in p.variants:
            status = 'in stock' if v.stock > 0 else 'sold out'
            variant_bits.append(f'{v.title} (${v.price}, {status})')
        variants_text = '; '.join(variant_bits) if variant_bits else 'no variants'
        lines.append(f'- {p.title}: {variants_text}')
    return '\n'.join(lines)


def build_system_prompt(product_context):
    return (
        f'You are a sales assistant for an online clothing and beauty store. '
        f'Your tone is {BRAND_TONE}. '
        f'You ONLY answer questions about the store products listed below. '
        f'If asked about anything unrelated, politely say you can only help with the store products. '
        f'Never invent products, prices, or stock. Use ONLY the data below. '
        f'Keep replies short and natural, like a real DM.\n\n'
        f'PRODUCTS:\n{product_context}'
    )


def generate_reply(customer_message):
    db = SessionLocal()
    product_context = get_product_context(db)
    db.close()

    system_prompt = build_system_prompt(product_context)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': customer_message},
        ],
    )
    return response.choices[0].message.content
