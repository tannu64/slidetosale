from datetime import datetime, timedelta
from sqlalchemy import func
from database import SessionLocal
import models


def get_analytics(merchant_id=1, days=30):
    db = SessionLocal()
    since = datetime.now() - timedelta(days=days)

    # Conversations belonging to this merchant.
    convo_ids = [
        c.id for c in db.query(models.Conversation)
        .filter(models.Conversation.merchant_id == merchant_id).all()
    ]

    def count(event_type):
        return db.query(models.Event).filter(
            models.Event.conversation_id.in_(convo_ids),
            models.Event.event_type == event_type,
            models.Event.created_at >= since,
        ).count()

    dm_volume = count('dm_received')
    checkout_starts = count('checkout_generated')
    checkout_clicks = count('checkout_clicked')
    orders = count('purchase')

    # High-intent messages in the window.
    high_intent = db.query(models.Message).join(
        models.Conversation, models.Message.conversation_id == models.Conversation.id
    ).filter(
        models.Conversation.merchant_id == merchant_id,
        models.Message.intent == 'high',
        models.Message.created_at >= since,
    ).count()

    # Total revenue from purchases in the window.
    revenue = db.query(func.coalesce(func.sum(models.Event.order_value), 0.0)).filter(
        models.Event.conversation_id.in_(convo_ids),
        models.Event.event_type == 'purchase',
        models.Event.created_at >= since,
    ).scalar()

    db.close()

    return {
        'days': days,
        'dm_volume': dm_volume,
        'high_intent': high_intent,
        'checkout_starts': checkout_starts,
        'checkout_clicks': checkout_clicks,
        'orders': orders,
        'revenue': round(float(revenue), 2),
    }
