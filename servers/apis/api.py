from fastapi import Depends, HTTPException, APIRouter, status, Request, Form
from sqlalchemy.orm import Session
from servers.models import UserServer
from app.database import get_db
from users import models
from fastapi.responses import RedirectResponse
from app.security import get_current_user_from_cookie

router = APIRouter(
    prefix="/servers",
    tags=["servers"]
)

@router.post("/create")
async def create_server(
    request: Request,
    name: str = Form(...),
    url: str = Form(...),
    db: Session = Depends(get_db)
):
    email = get_current_user_from_cookie(request)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = db.query(models.User).filter(models.User.email == email).first()
    server = UserServer(
        user_id=user.id, 
        server_name=name,
        server_url=url
    )
    try:
        db.add(server)
        db.commit()
        db.refresh(server)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)