from database import SessionLocal
import models


def log_event(conversation_id, event_type, order_value=None):
    db = SessionLocal()
    event = models.Event(
        conversation_id=conversation_id,
        event_type=event_type,
        order_value=order_value,
    )
    db.add(event)
    db.commit()
    db.close()
