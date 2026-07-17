from database import SessionLocal
import models


def log_event(conversation_id, event_type, order_value=None, checkout_url=None):
    db = SessionLocal()
    event = models.Event(
        conversation_id=conversation_id,
        event_type=event_type,
        order_value=order_value,
        checkout_url=checkout_url,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    event_id = event.id
    db.close()
    return event_id