from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging import setup_logging
from app.api.routes import auth, users

setup_logging()

# Create tables on startup (use Alembic for production migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# Health / smoke-test endpoint
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "version": settings.APP_VERSION}


# Domain routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
