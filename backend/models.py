from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float,
    DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from database import Base


class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, index=True)
    ig_account = Column(String, nullable=True)      # Instagram handle
    shop_domain = Column(String, nullable=True)     # Shopify store domain
    ai_enabled = Column(Boolean, default=True)      # the on/off switch
    created_at = Column(DateTime, server_default=func.now())

    conversations = relationship("Conversation", back_populates="merchant")
    products = relationship("Product", back_populates="merchant")


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"))
    customer_id = Column(String, index=True)        # the Instagram user we are talking to
    created_at = Column(DateTime, server_default=func.now())

    merchant = relationship("Merchant", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    events = relationship("Event", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    sender = Column(String)                          # "customer" or "assistant"
    text = Column(Text)
    intent = Column(String, nullable=True)           # high / medium / low
    created_at = Column(DateTime, server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
    mentions = relationship("ProductMention", back_populates="message")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"))
    shopify_id = Column(String, index=True)          # id of the product in Shopify
    title = Column(String)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)

    merchant = relationship("Merchant", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product")
    mentions = relationship("ProductMention", back_populates="product")


class ProductVariant(Base):
    __tablename__ = "product_variants"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    shopify_variant_id = Column(String, index=True)
    title = Column(String)                            # e.g. "Medium / Black"
    price = Column(Float, nullable=True)
    stock = Column(Integer, default=0)

    product = relationship("Product", back_populates="variants")


class ProductMention(Base):
    __tablename__ = "product_mentions"
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime, server_default=func.now())

    message = relationship("Message", back_populates="mentions")
    product = relationship("Product", back_populates="mentions")


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    event_type = Column(String)                      # dm_received, checkout_generated, purchase, etc.
    order_value = Column(Float, nullable=True)       # filled in only for purchase events
    created_at = Column(DateTime, server_default=func.now())

    conversation = relationship("Conversation", back_populates="events")
