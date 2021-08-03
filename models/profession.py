from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.types import String
from models.base import Base

class Profession(Base):
    __tablename__ = 'profession'
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String,nullable = False)
    description = Column(String, nullable=True)
    recipes = relationship("Recipe")