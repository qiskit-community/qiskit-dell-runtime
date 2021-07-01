from typing import Text
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from sqlalchemy.orm import declarative_base, registry
from dataclasses import dataclass
from sqlalchemy import MetaData
from sqlalchemy.sql.sqltypes import TEXT

from .base import Base

@dataclass
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(64))