from app.core.database import SessionLocal


# db connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
