from fastapi import Depends, HTTPException, APIRouter, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from users import models
from app.database import get_db
from typing import List
from app.config import templates
from argon2 import PasswordHasher
from app.security import create_access_token


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/register")
async def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Validation
    if len(password) < 6:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Password too short!"})
    
    # 2. Check for existing user 
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Email already registered!"})

    # 3. Hash and Save
    hashed_password = PasswordHasher().hash(password)
    db_user = models.User(name=name, email=email, password=hashed_password)
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Database error. Try again."})

    return RedirectResponse(url="/signin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/login")
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Fetch user by email
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return templates.TemplateResponse("signin.html", {"request": request, "error": "Invalid credentials!"})
    
    # 2. Verify password
    try:
        PasswordHasher().verify(user.password, password)
    except:
        return templates.TemplateResponse("signin.html", {"request": request, "error": "Invalid credentials!"})
    
    # 3. Create JWT token
    access_token = create_access_token(data={"sub": user.email})

    # 4. Successful login (Setting cookie and redirecting)
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

