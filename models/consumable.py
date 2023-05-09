from sqlalchemy.orm import relationship
from models.base import Base
from sqlalchemy import Column
from sqlalchemy.types import Text, Integer, String


class Consumable(Base):
    __tablename__='consumable'
    
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    rarity = Column(String, nullable = False)
    level = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    effets = Column(Text, nullable=False)
    
    recipes = relationship('Recipe', back_populates='consumable')
    ingredients = relationship('Ingredient', back_populates='consumable')
