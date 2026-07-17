import os
import hmac
import hashlib
import base64
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from database import get_db
import models
import sync
import search
import orchestrator
import events
import conversations

load_dotenv()
BASE_URL = 'http://127.0.0.1:8000'
WEBHOOK_SECRET = os.getenv('SHOPIFY_WEBHOOK_SECRET', '')

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    sync.sync_products()
    scheduler.add_job(sync.sync_products, 'interval', minutes=30)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


class IncomingDM(BaseModel):
    customer_id: str
    text: str


def verify_shopify_webhook(body: bytes, hmac_header: str) -> bool:
    if not hmac_header:
        return False
    digest = hmac.new(WEBHOOK_SECRET.encode('utf-8'), body, hashlib.sha256).digest()
    computed = base64.b64encode(digest).decode('utf-8')
    return hmac.compare_digest(computed, hmac_header)


@app.get('/')
def read_root():
    return {'message': 'SlideToSale backend is alive'}


@app.post('/simulate-dm')
def simulate_dm(dm: IncomingDM, db: Session = Depends(get_db)):
    # Find or create a conversation for this customer (always linked to merchant).
    conversation_id = conversations.get_or_create_conversation(dm.customer_id)

    customer_msg = models.Message(
        conversation_id=conversation_id,
        sender='customer',
        text=dm.text,
    )
    db.add(customer_msg)
    db.commit()
    db.refresh(customer_msg)
    events.log_event(conversation_id, 'dm_received')

    result = orchestrator.handle_message(dm.text)

    reply = result['reply']
    tracking_link = None

    if result['checkout_link']:
        event_id = events.log_event(
            conversation_id,
            'checkout_generated',
            checkout_url=result['checkout_link'],
        )
        tracking_link = f'{BASE_URL}/click/{event_id}'
        reply = reply.replace(result['checkout_link'], tracking_link)

    ai_msg = models.Message(
        conversation_id=conversation_id,
        sender='assistant',
        text=reply,
        intent=result['intent'],
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)
    events.log_event(conversation_id, 'intent_detected')

    return {
        'conversation_id': conversation_id,
        'reply': reply,
        'intent': result['intent'],
        'checkout_link': tracking_link,
    }


@app.get('/click/{event_id}')
def track_click(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if event is None or not event.checkout_url:
        return {'error': 'link not found'}
    events.log_event(event.conversation_id, 'checkout_clicked')
    return RedirectResponse(url=event.checkout_url)


@app.post('/webhooks/order')
async def order_webhook(request: Request):
    body = await request.body()
    hmac_header = request.headers.get('X-Shopify-Hmac-Sha256', '')

    if not verify_shopify_webhook(body, hmac_header):
        raise HTTPException(status_code=401, detail='Invalid webhook signature')

    order = json.loads(body)
    order_value = float(order.get('total_price', 0))
    conversation_id = 1
    for attr in order.get('note_attributes', []):
        if attr.get('name') == 'conversation_id':
            conversation_id = int(attr.get('value', 1))

    events.log_event(conversation_id, 'purchase', order_value=order_value)
    return {'status': 'purchase logged', 'value': order_value}


@app.get('/analytics')
def analytics_endpoint(days: int = 30):
    import analytics
    return analytics.get_analytics(merchant_id=1, days=days)


@app.post('/sync-products')
def sync_products_endpoint():
    sync.sync_products()
    return {'status': 'sync complete'}


@app.get('/search')
def search_endpoint(keyword: str, variant: str = None, db: Session = Depends(get_db)):
    results = search.search_products(db, keyword, variant)
    return {'count': len(results), 'results': results}
