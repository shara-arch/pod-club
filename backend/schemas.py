from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    name: str
    avatar: Optional[str] = None


class UserCreate(UserBase):
    id: str


class User(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: Optional[str] = None
    image_caption: Optional[str] = None
    message_type: str = "text"


class MessageCreate(MessageBase):
    id: str
    channel_id: str
    author_id: str


class MessageUpdate(BaseModel):
    content: Optional[str] = None
    image_caption: Optional[str] = None


class Message(MessageBase):
    id: str
    channel_id: str
    author_id: str
    author: User
    image_url: Optional[str] = None
    timestamp: datetime
    reply_count: int
    thread_root_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class ChannelBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: bool = False
    category: Optional[str] = None


class ChannelCreate(ChannelBase):
    id: str
    community_id: str


class Channel(ChannelBase):
    id: str
    community_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ThreadMessageBase(BaseModel):
    content: str


class ThreadMessageCreate(ThreadMessageBase):
    id: str
    thread_id: str
    author_id: str


class ThreadMessage(ThreadMessageBase):
    id: str
    thread_id: str
    author_id: str
    author: User
    image_url: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ThreadBase(BaseModel):
    root_message_id: str


class ThreadCreate(ThreadBase):
    id: str
    channel_id: str


class Thread(ThreadBase):
    id: str
    channel_id: str
    created_at: datetime
    replies: List[ThreadMessage]
    
    class Config:
        from_attributes = True


class MessageHistory(BaseModel):
    total_messages: int
    channels: List[Channel]
    date_range: dict
    
    class Config:
        from_attributes = True


class ImageUploadResponse(BaseModel):
    filename: str
    url: str
    size: int
    timestamp: datetime
