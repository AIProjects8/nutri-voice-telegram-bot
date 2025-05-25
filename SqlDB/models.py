from sqlalchemy import Column, Integer, String, Date, UUID, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy import text

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'))
    telegram_id = Column(BigInteger, unique=True)
    name = Column(String(255))
    date_of_birth = Column(Date)
    weight = Column(Integer)
    sex = Column(String(50)) 