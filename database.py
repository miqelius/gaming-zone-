import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# გარემოს ცვლადიდან ბაზის URL-ის წაკითხვა (Render PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gaming_zone.db")

# Render-ის postgres:// მისამართის გარდაქმნა postgresql:// -ად SQLAlchemy 2.0-ისთვის
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    device_type = Column(String)
    is_vip = Column(Boolean, default=False)
    status = Column(String, default="FREE")

class TournamentMatch(Base):
    __tablename__ = "tournament_matches"

    id = Column(Integer, primary_key=True, index=True)
    match_code = Column(String, unique=True)
    player1 = Column(String, default="TBD")
    player2 = Column(String, default="TBD")
    score1 = Column(Integer, default=0)
    score2 = Column(Integer, default=0)
    status = Column(String, default="SCHEDULED")

Base.metadata.create_all(bind=engine)

def seed_initial_data():
    db = SessionLocal()
    if db.query(Device).count() == 0:
        for i in range(1, 21):
            db.add(Device(name=f"PC-{i:02d}", device_type="PC", is_vip=False))
        for i in range(1, 9):
            db.add(Device(name=f"PC-VIP-{i:02d}", device_type="PC", is_vip=True))

        for i in range(1, 21):
            db.add(Device(name=f"PS5-{i:02d}", device_type="PS5", is_vip=False))
        for i in range(1, 9):
            db.add(Device(name=f"PS5-VIP-{i:02d}", device_type="PS5", is_vip=True))

        db.commit()
    db.close()

seed_initial_data()
