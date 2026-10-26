from fastapi import FastAPI
from src.core.database import engine, Base
from src.api.auth.models import User
from src.api.auth.routes import router as auth_router
from src.api.media.routes import router as media_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Hub")

app.include_router(auth_router)
app.include_router(media_router)
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def serve_test_page():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()