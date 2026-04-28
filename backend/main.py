from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import auth, categories, decisions, notes, products, projects, rooms
from core.config import settings
from models import Category, Decision, Product, Project, Room, User  # noqa: F401


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            handler.setFormatter(JsonFormatter())
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        root.addHandler(handler)
    root.setLevel(settings.log_level.upper())


configure_logging()

app = FastAPI(
    title="HomeLogicAI Backend",
    version="0.1.0",
    description="API for project planning, product research, and decision tracking.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(projects.router, tags=["projects"])
app.include_router(rooms.router, tags=["rooms"])
app.include_router(categories.router, tags=["categories"])
app.include_router(products.router, tags=["products"])
app.include_router(decisions.router, tags=["decisions"])
app.include_router(notes.router, tags=["notes"])


@app.on_event("startup")
async def on_startup() -> None:
    Path(settings.storage_path).mkdir(parents=True, exist_ok=True)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}
