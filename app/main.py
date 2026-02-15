import asyncio
from .config import settings
from .database import engine, Base
from fastapi import FastAPI, Request, Depends
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from .config import templates
from .database import get_db
from .security import get_current_user_from_cookie
from users.api.endpoints import auth
from servers.apis import api
from users import models
from servers.models import UserServer
from servers.worker import monitoring_loop
from fastapi.middleware.cors import CORSMiddleware


if settings.ENVIRONMENT == "production":
    try:
        Base.metadata.create_all(bind=engine)
        print("Production: Database tables verified/created.")
    except Exception as e:
        print(f"Migration error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Run the monitoring loop in the background
    worker_task = asyncio.create_task(monitoring_loop())
    yield
    # SHUTDOWN: Clean up
    worker_task.cancel()

app = FastAPI(title="PulseAPI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all our organized routes
app.include_router(auth.router)
app.include_router(api.router)

@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    # This tells the browser to always validate with the server
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/")
async def root(request: Request):
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/signin")
async def signin_page(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})


@app.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):

    email = get_current_user_from_cookie(request)
    if not email:
        # Redirect to login if token is missing or invalid
        return RedirectResponse(url="/signin?error=Please login first", status_code=303)

    user = db.query(models.User).filter(models.User.email == email).first()
    sites = db.query(UserServer).filter(UserServer.user_id == user.id).all()

    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "user": user, "sites": sites}
    )


@app.get("/create-server")
async def create_server_page(request: Request, db: Session = Depends(get_db)):
    email = get_current_user_from_cookie(request)
    if not email:
        # Redirect to login if token is missing or invalid
        return RedirectResponse(url="/signin?error=Please login first", status_code=303)
    return templates.TemplateResponse("create_server.html", {"request": request})
