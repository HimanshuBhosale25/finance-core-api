from app.db.session import SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.core.security import hash_password

def seed():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@finance.com").first()
        if existing:
            print("Admin already exists — skipping.")
            return

        admin = User(
            name="Super Admin",
            email="admin@finance.com",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Admin created → id={admin.id}, email={admin.email}, role={admin.role}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()