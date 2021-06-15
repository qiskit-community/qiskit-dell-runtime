from typing import Text
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from sqlalchemy.orm import declarative_base, registry
from dataclasses import dataclass
from sqlalchemy import MetaData
from sqlalchemy.sql.sqltypes import TEXT

from .base import Base

@dataclass
class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    job_id = Column(String(64))
    data = Column(TEXT)
    creation_date = Column(DateTime)
