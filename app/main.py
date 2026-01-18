from fastapi import FastAPI
from users.api.endpoints import auth
from app.database import engine
from users import models


app = FastAPI(title="PulseAPI", version="1.0.0")

# Include all our organized routes
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "PulseAPI is online"}
