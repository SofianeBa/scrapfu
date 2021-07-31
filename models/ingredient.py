
from sqlalchemy.types import String
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column
from models.base import Base

class Ingredient(Base):
    __tablename__ = 'ingredient'
    recipe_id = Column(ForeignKey('recipe.id'), primary_key=True)
    resource_id = Column(ForeignKey('resource.id'), primary_key=True) 
    quantity = Column(String, nullable=False)
    recipe = relationship('Recipe',back_populates='resources')
    resource = relationship('Resource',back_populates='recipes')
