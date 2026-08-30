from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("Message", back_populates="author")
    thread_messages = relationship("ThreadMessage", back_populates="author")


class Channel(Base):
    __tablename__ = "channels"
    
    id = Column(String, primary_key=True)
    community_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_private = Column(Boolean, default=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("Message", back_populates="channel", cascade="all, delete-orphan")
    threads = relationship("Thread", back_populates="channel", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    channel_id = Column(String, ForeignKey("channels.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    image_caption = Column(String, nullable=True)
    message_type = Column(String, default="text")  # text, image, episode-share, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    reply_count = Column(Integer, default=0)
    thread_root_id = Column(String, ForeignKey("threads.id"), nullable=True)
    
    channel = relationship("Channel", back_populates="messages")
    author = relationship("User", back_populates="messages")
    thread = relationship("Thread", back_populates="root_message_ref", uselist=False)


class Thread(Base):
    __tablename__ = "threads"
    
    id = Column(String, primary_key=True)
    channel_id = Column(String, ForeignKey("channels.id"), nullable=False)
    root_message_id = Column(String, ForeignKey("messages.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    channel = relationship("Channel", back_populates="threads")
    root_message_ref = relationship("Message", back_populates="thread", uselist=False)
    replies = relationship("ThreadMessage", back_populates="thread", cascade="all, delete-orphan")


class ThreadMessage(Base):
    __tablename__ = "thread_messages"
    
    id = Column(String, primary_key=True)
    thread_id = Column(String, ForeignKey("threads.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    thread = relationship("Thread", back_populates="replies")
    author = relationship("User", back_populates="thread_messages")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
