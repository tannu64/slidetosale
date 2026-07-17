from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler

from database import get_db
import models
import sync
import search
import orchestrator
import events

BASE_URL = 'http://127.0.0.1:8000'

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
    conversation_id: int
    text: str


@app.get('/')
def read_root():
    return {'message': 'SlideToSale backend is alive'}


@app.post('/simulate-dm')
def simulate_dm(dm: IncomingDM, db: Session = Depends(get_db)):
    customer_msg = models.Message(
        conversation_id=dm.conversation_id,
        sender='customer',
        text=dm.text,
    )
    db.add(customer_msg)
    db.commit()
    db.refresh(customer_msg)
    events.log_event(dm.conversation_id, 'dm_received')

    result = orchestrator.handle_message(dm.text)

    reply = result['reply']
    tracking_link = None

    # If a checkout link was generated, store it on the event and build a tracking link.
    if result['checkout_link']:
        event_id = events.log_event(
            dm.conversation_id,
            'checkout_generated',
            checkout_url=result['checkout_link'],
        )
        tracking_link = f'{BASE_URL}/click/{event_id}'
        # Replace the raw Shopify link in the reply with our tracking link.
        reply = reply.replace(result['checkout_link'], tracking_link)

    ai_msg = models.Message(
        conversation_id=dm.conversation_id,
        sender='assistant',
        text=reply,
        intent=result['intent'],
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)
    events.log_event(dm.conversation_id, 'intent_detected')

    return {
        'customer_message_id': customer_msg.id,
        'reply': reply,
        'intent': result['intent'],
        'checkout_link': tracking_link,
    }


@app.get('/click/{event_id}')
def track_click(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if event is None or not event.checkout_url:
        return {'error': 'link not found'}
    # Log the click, then redirect to the real Shopify checkout.
    events.log_event(event.conversation_id, 'checkout_clicked')
    return RedirectResponse(url=event.checkout_url)


@app.post('/sync-products')
def sync_products_endpoint():
    sync.sync_products()
    return {'status': 'sync complete'}


@app.get('/search')
def search_endpoint(keyword: str, variant: str = None, db: Session = Depends(get_db)):
    results = search.search_products(db, keyword, variant)
    return {'count': len(results), 'results': results}
