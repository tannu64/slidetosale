from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
import models

app = FastAPI()


# Describes the shape of an incoming DM. FastAPI checks the request matches this.
class IncomingDM(BaseModel):
    conversation_id: int
    text: str


@app.get("/")
def read_root():
    return {"message": "SlideToSale backend is alive"}


# The DM simulator endpoint: receives a message and stores it in the database.
@app.post("/simulate-dm")
def simulate_dm(dm: IncomingDM, db: Session = Depends(get_db)):
    new_message = models.Message(
        conversation_id=dm.conversation_id,
        sender="customer",
        text=dm.text,
    )
    db.add(new_message)      # stage the new row
    db.commit()              # save it permanently
    db.refresh(new_message)  # reload it so we get its new id
    return {
        "status": "stored",
        "message_id": new_message.id,
        "text": new_message.text,
    }
