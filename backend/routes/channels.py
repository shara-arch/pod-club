from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db, Channel
from schemas import Channel as ChannelSchema, ChannelCreate

router = APIRouter(prefix="/api/channels", tags=["channels"])


@router.post("/", response_model=ChannelSchema)
async def create_channel(
    channel: ChannelCreate,
    db: Session = Depends(get_db)
):
    """Create a new channel"""
    # Check if channel already exists
    existing = db.query(Channel).filter(Channel.id == channel.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Channel already exists")
    
    db_channel = Channel(
        id=channel.id,
        community_id=channel.community_id,
        name=channel.name,
        description=channel.description,
        is_private=channel.is_private,
        category=channel.category
    )
    
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    
    return db_channel


@router.get("/", response_model=List[ChannelSchema])
async def list_channels(
    community_id: str = None,
    db: Session = Depends(get_db)
):
    """List all channels or channels in a specific community"""
    query = db.query(Channel)
    
    if community_id:
        query = query.filter(Channel.community_id == community_id)
    
    channels = query.all()
    return channels


@router.get("/{channel_id}", response_model=ChannelSchema)
async def get_channel(
    channel_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific channel"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    return channel


@router.patch("/{channel_id}", response_model=ChannelSchema)
async def update_channel(
    channel_id: str,
    name: str = None,
    description: str = None,
    is_private: bool = None,
    category: str = None,
    db: Session = Depends(get_db)
):
    """Update a channel"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    if name is not None:
        channel.name = name
    if description is not None:
        channel.description = description
    if is_private is not None:
        channel.is_private = is_private
    if category is not None:
        channel.category = category
    
    db.commit()
    db.refresh(channel)
    
    return channel


@router.delete("/{channel_id}", status_code=204)
async def delete_channel(
    channel_id: str,
    db: Session = Depends(get_db)
):
    """Delete a channel and all its messages"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    db.delete(channel)
    db.commit()
    
    return None
