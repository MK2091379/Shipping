import os
import bcrypt
from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# در فایل database.py
DB_HOST = os.getenv('DB_HOST', 'localhost') # اگر در داکر نباشد، پیش‌فرض لکال‌هوست
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# ساخت کانکشن استرینگ با استفاده از نام سرویس (db)
DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="user") # 'admin' یا 'user'
    created_at = Column(DateTime, default=datetime.utcnow)
    
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # مثلا 'SEARCH'
    target_value = Column(String)  # شماره کانتینر جست‌وجو شده
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# تابعی برای ساخت دستی ادمین (میتوانی یکبار اجرا کنی)
def create_admin(username, password, full_name):
    db = SessionLocal()
    existing_admin = db.query(User).filter(User.username == username).first()
    if not existing_admin:
        hashed_pw = hash_password(password)
        admin = User(username=username, password_hash=hashed_pw, full_name=full_name, role="admin")
        db.add(admin)
        db.commit()
    db.close()