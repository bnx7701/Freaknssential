
from fastapi import FastAPI

from backend.database.db import Base, engine
from backend.models import db_models
from backend.routes import agents, actions, approvals, logs, auth

# Create all database tables, including UsedNonce
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Freaknssential API",
    description="Security gateway for autonomous AI agents",
    version="1.0.0",
)

# Register all API routers
app.include_router(agents.router)
app.include_router(actions.router)
app.include_router(approvals.router)
app.include_router(logs.router)
app.include_router(auth.router)


@app.get("/")
def home():
    return {
        "name": "Freaknssential",
        "status": "running",
        "message": "AI Agent Security Gateway is online",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
