from contextlib import asynccontextmanager
from app.api import router
from fastapi import FastAPI
from sqlalchemy import select

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Room


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Room).limit(1)) is None:
            db.add_all([Room(name=name) for name in settings.seed_rooms])
            db.commit()
    yield


app = FastAPI(title="Night Care Room Monitor", lifespan=lifespan)
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}