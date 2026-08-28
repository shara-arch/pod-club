from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db, User
from schemas import User as UserSchema, UserCreate

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserSchema)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user"""
    # Check if user already exists
    existing = db.query(User).filter(User.id == user.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")
    
    db_user = User(
        id=user.id,
        name=user.name,
        avatar=user.avatar
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get("/", response_model=List[UserSchema])
async def list_users(db: Session = Depends(get_db)):
    """List all users"""
    users = db.query(User).all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.patch("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: str,
    name: str = None,
    avatar: str = None,
    db: Session = Depends(get_db)
):
    """Update a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if name is not None:
        user.name = name
    if avatar is not None:
        user.avatar = avatar
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return None
