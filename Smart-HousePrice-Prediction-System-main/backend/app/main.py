import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router
from app.core.startup import on_startup

app = FastAPI(
    title="Real Estate AI Search",
    version="1.0.0"
)

# Enable CORS (still useful for local development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. API Routes (prefixed with /api)
app.include_router(router, prefix="/api")

# 2. Serve Static Files (Frontend)
static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

# If the static folder exists (built by Render), serve it
if os.path.exists(static_path):
    # Serve index.html at the root
    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(static_path, "index.html"))

    # Mount the rest of the assets (js, css, etc.)
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

    # Catch-all for React Router navigation
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        if not full_path.startswith("api"):
            return FileResponse(os.path.join(static_path, "index.html"))

@app.on_event("startup")
def startup():
    on_startup()