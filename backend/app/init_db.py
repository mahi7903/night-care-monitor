import re

from sqlalchemy import select, text

from app.auth import hash_password
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Room, StaffUser

SAFE_NAME = re.compile(r"^[A-Za-z0-9_]+$")


def seed():
    with SessionLocal() as db:
        if db.scalar(select(Room).limit(1)) is None:
            db.add_all([Room(name=name) for name in settings.seed_rooms])
        username, password = settings.seed_staff_username, settings.seed_staff_password
        if username and password:
            exists = db.scalar(select(StaffUser).where(StaffUser.username == username))
            if exists is None:
                db.add(StaffUser(username=username, password_hash=hash_password(password)))
        db.commit()


def ensure_app_user(user: str, password: str):
    if not (SAFE_NAME.match(user) and SAFE_NAME.match(password)):
        raise ValueError("APP_DB_USER and APP_DB_PASSWORD must be letters, numbers or underscores")

    with engine.begin() as conn:
        exists = conn.scalar(text("SELECT 1 FROM pg_roles WHERE rolname = :u"), {"u": user})
        action = "ALTER" if exists else "CREATE"
        conn.execute(text(f"{action} ROLE {user} LOGIN PASSWORD '{password}'"))
        db_name = conn.scalar(text("SELECT current_database()"))
        conn.execute(text(f'GRANT CONNECT ON DATABASE "{db_name}" TO {user}'))
        conn.execute(text(f"GRANT USAGE ON SCHEMA public TO {user}"))
        conn.execute(text(f"GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO {user}"))
        conn.execute(text(f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {user}"))


def main():
    Base.metadata.create_all(engine)
    seed()
    if settings.app_db_user and settings.app_db_password:
        ensure_app_user(settings.app_db_user, settings.app_db_password)
    print("Database ready")


if __name__ == "__main__":
    main()