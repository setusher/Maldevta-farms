from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True, nullable=False)
    user_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    context = Column(JSON, default={})  # Store conversation context
    status = Column(String, default="active")  # active, completed, abandoned

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, index=True)
    phone_number = Column(String, index=True)
    message_sid = Column(String, nullable=True)  # Nullable, not unique
    direction = Column(String)  # inbound, outbound
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_type = Column(String, default="text")  # text, image, document

class ToolCall(Base):
    __tablename__ = "tool_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, index=True)
    tool_name = Column(String)
    input_data = Column(JSON)
    output_data = Column(JSON)
    success = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text, nullable=True)

class AgentMemory(Base):
    __tablename__ = "agent_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True)
    key = Column(String)  # name, preferences, last_booking, etc.
    value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/whatsapp_agent")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()