from fastapi import Depends, HTTPException, APIRouter, status, Request, Form, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from servers.models import ServerAnalytics, UserServer
from app.database import get_db
from users import models
from app.config import templates
from fastapi.responses import RedirectResponse
from app.security import get_current_user_from_cookie
from servers.websocket_manager import manager

router = APIRouter(
    prefix="/servers",
    tags=["servers"]
)

@router.post("/create")
async def create_server(
    request: Request,
    name: str = Form(...),
    url: str = Form(...),
    interval: int = Form(...),
    db: Session = Depends(get_db)
):
    email = get_current_user_from_cookie(request)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = db.query(models.User).filter(models.User.email == email).first()

    if interval < 10:
        return templates.TemplateResponse(
            "create_server.html",
            {"request": request, "error": "Interval must be at least 10 seconds"}
        )
    
    server = UserServer(
        user_id=user.id, 
        server_name=name,
        server_url=url,
        interval_seconds=interval
    )
    try:
        db.add(server)
        db.commit()
        db.refresh(server)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/delete/{server_id}")
async def delete_server(
    request: Request,
    server_id: int,
    db: Session = Depends(get_db)
):
    email = get_current_user_from_cookie(request)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = db.query(models.User).filter(models.User.email == email).first()
    server = db.query(UserServer).filter(UserServer.id == server_id, UserServer.user_id == user.id).first()
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    try:
        db.delete(server)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/edit/{server_id}")
async def show_edit_form(request: Request, server_id: int, db: Session = Depends(get_db)):
    email = get_current_user_from_cookie(request)
    if not email:
        return RedirectResponse(url="/signin", status_code=303)
        
    user = db.query(models.User).filter(models.User.email == email).first()
    server = db.query(UserServer).filter(UserServer.id == server_id, UserServer.user_id == user.id).first()
    
    if not server:
        return RedirectResponse(url="/dashboard", status_code=303)

    return templates.TemplateResponse("edit_server.html", {"request": request, "user": user, "server": server})

@router.post("/edit/{server_id}")
async def edit_server(
    request: Request,
    server_id: int,
    name: str = Form(...),
    url: str = Form(...),
    interval: int = Form(...),
    db: Session = Depends(get_db)
):
    email = get_current_user_from_cookie(request)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = db.query(models.User).filter(models.User.email == email).first()
    server = db.query(UserServer).filter(UserServer.id == server_id, UserServer.user_id == user.id).first()
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    
    if interval < 10:
        return templates.TemplateResponse(
            "edit_server.html",
            {"request": request, "server": server, "error": "Interval must be at least 10 seconds"}
        )
    
    server.server_name = name
    server.server_url = url
    server.interval_seconds = interval
    try:
        db.commit()
        db.refresh(server)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/analytics/{server_id}")
async def get_analytics(server_id: int, request: Request, db: Session = Depends(get_db)):

    email = get_current_user_from_cookie(request)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    server = db.query(UserServer).filter(UserServer.id == server_id, UserServer.user_id == user.id).first()
    last_10 = db.query(ServerAnalytics).filter(ServerAnalytics.server_id == server_id).order_by(ServerAnalytics.created_at.desc()).limit(10).all()
    
    return templates.TemplateResponse("analytics.html", {
        "request": request, 
        "server": server,
        "labels": last_10,
        "user": user
    })


@router.websocket("/ws/server/{server_id}")
async def websocket_endpoint(websocket: WebSocket, server_id: int):
    await manager.connect(websocket, server_id)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text() 
    except WebSocketDisconnect as e:
        manager.disconnect(websocket, server_id)

