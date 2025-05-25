from sqlalchemy import Column, Integer, String, Date, UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(Integer, unique=True)
    name = Column(String(255))
    date_of_birth = Column(Date)
    weight = Column(Integer)
    sex = Column(String(50)) 