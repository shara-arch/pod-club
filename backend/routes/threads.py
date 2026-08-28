from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import List

from database import get_db, Thread, ThreadMessage, Message, User, Channel
from schemas import Thread as ThreadSchema, ThreadMessage as ThreadMessageSchema, ThreadMessageCreate
from utils import generate_id

router = APIRouter(prefix="/api/threads", tags=["threads"])


@router.post("/", response_model=ThreadSchema)
async def create_thread(
    channel_id: str,
    root_message_id: str,
    db: Session = Depends(get_db)
):
    """Create a new thread from a message"""
    # Verify channel exists
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Verify message exists
    message = db.query(Message).filter(Message.id == root_message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Check if thread already exists for this message
    existing_thread = db.query(Thread).filter(
        Thread.root_message_id == root_message_id
    ).first()
    if existing_thread:
        return existing_thread
    
    # Create thread
    thread_id = generate_id("t")
    thread = Thread(
        id=thread_id,
        channel_id=channel_id,
        root_message_id=root_message_id,
        created_at=datetime.utcnow()
    )
    
    # Update message with thread reference
    message.thread_root_id = thread_id
    
    db.add(thread)
    db.commit()
    db.refresh(thread)
    
    return thread


@router.get("/{thread_id}", response_model=ThreadSchema)
async def get_thread(
    thread_id: str,
    db: Session = Depends(get_db)
):
    """Get a thread with all its replies"""
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return thread


@router.post("/{thread_id}/reply", response_model=ThreadMessageSchema)
async def add_thread_reply(
    thread_id: str,
    author_id: str,
    content: str,
    db: Session = Depends(get_db)
):
    """Add a reply to a thread"""
    # Verify thread exists
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Verify user exists
    user = db.query(User).filter(User.id == author_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create thread message
    message_id = generate_id("tm")
    thread_message = ThreadMessage(
        id=message_id,
        thread_id=thread_id,
        author_id=author_id,
        content=content,
        timestamp=datetime.utcnow()
    )
    
    # Increment reply count on root message
    root_message = thread.root_message_ref
    if root_message:
        root_message.reply_count = len(thread.replies) + 1
    
    db.add(thread_message)
    db.commit()
    db.refresh(thread_message)
    
    return thread_message


@router.get("/{thread_id}/replies", response_model=List[ThreadMessageSchema])
async def get_thread_replies(
    thread_id: str,
    db: Session = Depends(get_db)
):
    """Get all replies in a thread"""
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    replies = db.query(ThreadMessage)\
        .filter(ThreadMessage.thread_id == thread_id)\
        .order_by(ThreadMessage.timestamp)\
        .all()
    
    return replies


@router.patch("/reply/{reply_id}", response_model=ThreadMessageSchema)
async def update_thread_reply(
    reply_id: str,
    content: str = None,
    db: Session = Depends(get_db)
):
    """Update a thread reply"""
    reply = db.query(ThreadMessage).filter(ThreadMessage.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    if content is not None:
        reply.content = content
    
    db.commit()
    db.refresh(reply)
    
    return reply


@router.delete("/reply/{reply_id}", status_code=204)
async def delete_thread_reply(
    reply_id: str,
    db: Session = Depends(get_db)
):
    """Delete a thread reply"""
    reply = db.query(ThreadMessage).filter(ThreadMessage.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    # Decrement reply count on root message
    thread = reply.thread
    root_message = thread.root_message_ref
    if root_message and root_message.reply_count > 0:
        root_message.reply_count -= 1
    
    db.delete(reply)
    db.commit()
    
    return None
