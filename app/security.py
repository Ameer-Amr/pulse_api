import jwt
from fastapi import Request
from .config import settings
from datetime import datetime, timedelta, timezone
from typing import Optional


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    # Calculate expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add expiration ('exp') to the payload
    to_encode.update({"exp": expire})
    
    # Sign the token with your Secret Key
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        token = token.replace("Bearer ", "")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except jwt.PyJWTError:
        return None

