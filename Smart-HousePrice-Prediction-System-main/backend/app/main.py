# app/main.py

from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.startup import on_startup

app = FastAPI(
    title="Real Estate AI Search",
    version="1.0.0"
)

# Enable CORS for frontend integration
# NOTE: Cannot use allow_origins=["*"] with allow_credentials=True
# So we explicitly list frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
def startup():
    on_startup()