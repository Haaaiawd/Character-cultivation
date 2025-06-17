# app/models/base.py
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from typing import Any

@as_declarative()
class Base:
    id: Any # All models will have an id
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s" # e.g. User -> users

class CustomBase(Base): # Renamed to avoid conflict if Base is used directly elsewhere
    __abstract__ = True # Make sure this is an abstract base class
    id = Column(Integer, primary_key=True, index=True)
