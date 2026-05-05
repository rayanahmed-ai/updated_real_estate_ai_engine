# app/core/startup.py

from app.storage.database import engine
from app.storage.models import Base

def on_startup():
    """
    Placeholder for:
    - DB init
    - Scheduler start
    """
    print("🚀 Application starting...")
    try:
        # checkfirst=True is default, but we wrap in try/except for extra safety with multiple workers
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("📊 Database tables verified")
    except Exception as e:
        print(f"⚠️ Database initialization skipped (likely already exists): {e}")