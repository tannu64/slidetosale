from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler

from database import get_db
import models
import sync
import search
import orchestrator

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
    # 1. Store the incoming customer message.
    customer_msg = models.Message(
        conversation_id=dm.conversation_id,
        sender='customer',
        text=dm.text,
    )
    db.add(customer_msg)
    db.commit()
    db.refresh(customer_msg)

    # 2. Run the full AI pipeline.
    result = orchestrator.handle_message(dm.text)

    # 3. Store the AI reply, tagged with the detected intent.
    ai_msg = models.Message(
        conversation_id=dm.conversation_id,
        sender='assistant',
        text=result['reply'],
        intent=result['intent'],
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    # 4. Return everything.
    return {
        'customer_message_id': customer_msg.id,
        'reply': result['reply'],
        'intent': result['intent'],
        'checkout_link': result['checkout_link'],
    }


@app.post('/sync-products')
def sync_products_endpoint():
    sync.sync_products()
    return {'status': 'sync complete'}


@app.get('/search')
def search_endpoint(keyword: str, variant: str = None, db: Session = Depends(get_db)):
    results = search.search_products(db, keyword, variant)
    return {'count': len(results), 'results': results}
