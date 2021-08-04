from sqlalchemy.orm import relation, relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, Text, String
from .monsterresource import MonsterResource
from .ingredient import Ingredient
from .base import Base

# Resource model class - Gathers id,name,type, and description. Associates resources to monsters that drop it and recipes that use it
class Resource(Base):
    __tablename__='resource'
    id = Column(Integer, primary_key=True, autoincrement=False)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    level = Column(Integer, nullable=False)
    monsters = relationship("MonsterResource", back_populates="resource")
    recipes = relationship("Ingredient", back_populates="resource")