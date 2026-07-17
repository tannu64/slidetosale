from database import SessionLocal
import models


def get_or_create_conversation(customer_id, merchant_id=1):
    db = SessionLocal()
    convo = (
        db.query(models.Conversation)
        .filter(
            models.Conversation.customer_id == customer_id,
            models.Conversation.merchant_id == merchant_id,
        )
        .first()
    )
    if convo is None:
        convo = models.Conversation(
            customer_id=customer_id,
            merchant_id=merchant_id,
        )
        db.add(convo)
        db.commit()
        db.refresh(convo)
    convo_id = convo.id
    db.close()
    return convo_id
