import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, inspect
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# Load environment variables
load_dotenv()

# Choose DB based on environment
ENV = os.getenv("ENV", "local")  # default 'local' if not set

if ENV == "local":
    DATABASE_URL = os.getenv("DATABASE_URL_LAPTOP")
else:  # production (Railway)
    DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Database URL is not set in .env file.")

# Engine & Session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class UserRequest(Base):
    __tablename__ = "user_requests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)
    business_type = Column(String, nullable=False)
    location = Column(String, nullable=False)
    purpose = Column(Text, nullable=False)
    days_needed = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    chat_history = relationship("ChatHistory", back_populates="user_request", cascade="all, delete-orphan")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    user_request_id = Column(Integer, ForeignKey("user_requests.id", ondelete="CASCADE"), nullable=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_request = relationship("UserRequest", back_populates="chat_history")

# Initialize DB
def init_db():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    models = [UserRequest, ChatHistory]
    for model in models:
        table_name = model.__tablename__
        if table_name not in existing_tables:
            model.__table__.create(bind=engine)
            print(f"✅ Table '{table_name}' created successfully!")
        else:
            print(f"ℹ Table '{table_name}' already exists.")

# Run only if executed directly
if __name__ == "__main__":
    init_db()
