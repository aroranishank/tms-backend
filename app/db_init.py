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
            hashed_password=hashed_pw,
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        print("✅ Default admin created (username=admin, password=admin123)")
    db.close()
