import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, transactions
from pathlib import Path

app = FastAPI()

static_path = os.getenv("FRONTEND_STATIC_PATH")
if static_path:
    static_path = Path(static_path)
    if static_path.exists() and static_path.is_dir():
        app.mount(
            "/static", StaticFiles(directory=static_path, html=False), name="static"
        )

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
# app.include_router(rules.router, prefix="/rules", tags=["rules"])
# app.include_router(upload.router, prefix="/upload-statement", tags=["upload"])


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
