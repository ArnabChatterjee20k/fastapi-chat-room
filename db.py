from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy import Column,String,Integer,select

class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    message = Column(String)


Base.metadata.create_all(bind=engine)


def add_message(message):
    db = SessionLocal()
    message = Messages(message=message)
    db.add(message)
    db.commit()


def get_all_messages():
    db = SessionLocal()
    stmt = select(Messages)
    results = db.execute(stmt).scalars().all()
    db.close()
    return results