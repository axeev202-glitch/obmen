from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    phone = Column(String(20))
    city = Column(String(100))
    rating = Column(Float, default=5.0)
    registration_date = Column(DateTime, default=datetime.utcnow)

class Advertisement(Base):
    __tablename__ = 'advertisements'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(200))
    description = Column(Text)
    condition = Column(Text)
    desired_exchange = Column(Text)
    photos = Column(Text)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)

class Exchange(Base):
    __tablename__ = 'exchanges'
    id = Column(Integer, primary_key=True)
    initiator_id = Column(Integer, ForeignKey('users.id'))
    responder_id = Column(Integer, ForeignKey('users.id'))
    advertisement_id = Column(Integer, ForeignKey('advertisements.id'))
    conditions = Column(Text)
    status = Column(String(50), default='pending')
    created_date = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    return SessionLocal()