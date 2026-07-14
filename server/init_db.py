from app.db.database import SessionLocal, Base
from app.models.models import User, Client, Action, AIExtracted, Video, PenTestResult, Tool, ToolVersion, TaskPlan, TaskTarget, Asset

def init_database():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=db.bind)
        print("Database tables created")
        
        existing = db.query(User).filter(User.username == "admin").first()
        if not existing:
            user = User(username="admin", password_hash="admin", role="admin")
            db.add(user)
            db.commit()
            print("Default user created: admin / admin")
        else:
            print("Default user already exists")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
