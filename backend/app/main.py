import os
import logging
# from app.logging import setup_logging

# Configure logging early so other modules (routers, auth, db) pick up config
# setup_logging()

from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, transactions, rules, actions
from app.routers import categories, tags
from app.db import DB

DB().get_instance()  # Initialize DB singleton

app = FastAPI()


logger = logging.getLogger(__name__)


@app.on_event("startup")
async def on_startup():
    logger.info("Application startup: Spending Frustration API")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Application shutdown")


static_path = os.getenv("FRONTEND_STATIC_PATH")
if static_path:
    static_path = Path(static_path)
    if static_path.exists() and static_path.is_dir():
        app.mount("/static", StaticFiles(directory=static_path, html=False), name="static")

# Allow CORS for local frontend

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(rules.router, prefix="/rules", tags=["rules"])
# app.include_router(upload.router, prefix="/upload-statement", tags=["upload"])
app.include_router(actions.router, prefix="/actions", tags=["actions"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])


@app.get("/")
async def root_index():
    """Serve React index.html if available, else minimal JSON."""
    index_path = static_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return {"message": "Spending Frustration API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
