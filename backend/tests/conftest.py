import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("JWT_SECRET", "test-only-secret-that-is-long-enough-123")
os.environ.setdefault("DEVICE_API_KEY", "test-device-key")

from app.auth import create_access_token, hash_password  # noqa: E402
from app.config import settings  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Room, StaffUser  # noqa: E402

engine = create_engine(TEST_DATABASE_URL)
TestingSession = sessionmaker(bind=engine, autoflush=False)


@pytest.fixture
def db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = TestingSession()
    session.add_all([Room(name="Room 1"), Room(name="Room 2")])
    session.commit()
    yield session
    session.close()


@pytest.fixture
def staff_user(db):
    user = StaffUser(username="nurse", password_hash=hash_password("correct-horse"))
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def anon_client(db, staff_user):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client(anon_client, staff_user):
    anon_client.headers.update({
        "Authorization": f"Bearer {create_access_token(staff_user)}",
        "X-API-Key": settings.device_api_key,
    })
    return anon_client