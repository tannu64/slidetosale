from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler

from database import get_db
import models
import sync

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts.
    sync.sync_products()                      # fresh data immediately
    scheduler.add_job(sync.sync_products, 'interval', minutes=30)
    scheduler.start()
    yield
    # Runs when the server shuts down.
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
    new_message = models.Message(
        conversation_id=dm.conversation_id,
        sender='customer',
        text=dm.text,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return {
        'status': 'stored',
        'message_id': new_message.id,
        'text': new_message.text,
    }


@app.post('/sync-products')
def sync_products_endpoint():
    sync.sync_products()
    return {'status': 'sync complete'}
