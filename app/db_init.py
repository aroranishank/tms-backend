from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import models, security

def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    # Check if admin exists
    admin = db.query(models.User).filter_by(username="admin").first()
    if not admin:
        hashed_pw = security.get_password_hash("admin123")
        admin_user = models.User(
            username="admin",
            email="admin@taskmanager.com",
            hashed_password=hashed_pw,
            user_type="admin"
        )
        db.add(admin_user)
        db.commit()
        print("✅ Default admin created (username=admin, password=admin123)")
    db.close()
