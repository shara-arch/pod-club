from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
from typing import List
import os

from database import get_db, Message, Channel, User, Thread, ThreadMessage
from schemas import Message as MessageSchema, MessageCreate, MessageUpdate, ImageUploadResponse
from utils import generate_id, save_image, delete_image, validate_image_file
from config import UPLOAD_FOLDER

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("/", response_model=MessageSchema)
async def create_message(
    channel_id: str,
    author_id: str,
    content: str = None,
    message_type: str = "text",
    image_caption: str = None,
    db: Session = Depends(get_db)
):
    """Create a new message in a channel"""
    # Verify channel exists
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Verify user exists
    user = db.query(User).filter(User.id == author_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create message
    message_id = generate_id("m")
    message = Message(
        id=message_id,
        channel_id=channel_id,
        author_id=author_id,
        content=content,
        message_type=message_type,
        image_caption=image_caption,
        timestamp=datetime.utcnow()
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message


@router.get("/{channel_id}", response_model=List[MessageSchema])
async def get_channel_messages(
    channel_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get messages from a channel"""
    # Verify channel exists
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    messages = db.query(Message)\
        .filter(Message.channel_id == channel_id)\
        .order_by(desc(Message.timestamp))\
        .limit(limit)\
        .offset(offset)\
        .all()
    
    return list(reversed(messages))  # Return in chronological order


@router.get("/{channel_id}/history", response_model=dict)
async def get_message_history(
    channel_id: str,
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get message history statistics for a channel"""
    # Verify channel exists
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    messages = db.query(Message)\
        .filter(
            and_(
                Message.channel_id == channel_id,
                Message.timestamp >= start_date
            )
        )\
        .all()
    
    # Group by date
    history_by_date = {}
    for message in messages:
        date_key = message.timestamp.date().isoformat()
        if date_key not in history_by_date:
            history_by_date[date_key] = []
        history_by_date[date_key].append({
            "id": message.id,
            "author": message.author.name,
            "content": message.content,
            "timestamp": message.timestamp.isoformat()
        })
    
    return {
        "channel_id": channel_id,
        "total_messages": len(messages),
        "date_range": {
            "from": start_date.date().isoformat(),
            "to": datetime.utcnow().date().isoformat()
        },
        "history_by_date": history_by_date
    }


@router.patch("/{message_id}", response_model=MessageSchema)
async def update_message(
    message_id: str,
    update_data: MessageUpdate,
    db: Session = Depends(get_db)
):
    """Update a message"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if update_data.content is not None:
        message.content = update_data.content
    if update_data.image_caption is not None:
        message.image_caption = update_data.image_caption
    
    db.commit()
    db.refresh(message)
    
    return message


@router.delete("/{message_id}", status_code=204)
async def delete_message(
    message_id: str,
    db: Session = Depends(get_db)
):
    """Delete a message"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Delete associated image if exists
    if message.image_url:
        delete_image(message.image_url)
    
    # Delete associated thread if this message is a thread root
    thread = db.query(Thread).filter(Thread.root_message_id == message_id).first()
    if thread:
        db.delete(thread)
    
    db.delete(message)
    db.commit()
    
    return None


@router.post("/{message_id}/upload-image", response_model=ImageUploadResponse)
async def upload_message_image(
    message_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an image for a message"""
    # Verify message exists
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Validate image
    is_valid, error_msg = validate_image_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Delete old image if exists
    if message.image_url and os.path.exists(message.image_url):
        delete_image(message.image_url)
    
    # Save new image
    try:
        filepath = save_image(file, message_id)
        message.image_url = filepath
        message.message_type = "image"
        
        db.commit()
        db.refresh(message)
        
        return ImageUploadResponse(
            filename=file.filename,
            url=f"/uploads/{os.path.basename(filepath)}",
            size=os.path.getsize(filepath),
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
