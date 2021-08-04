
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column
from models.base import Base

#Ingredient model class - Used for recipe and resource's many <-> many relationship. Adds quantity for reach ingredient in the recipe
class Ingredient(Base):
    __tablename__ = 'ingredient'
    recipe_id = Column(ForeignKey('recipe.id'), primary_key=True)
    resource_id = Column(ForeignKey('resource.id'), primary_key=True) 
    quantity = Column(Integer, nullable=False)
    recipe = relationship('Recipe',back_populates='resources')
    resource = relationship('Resource',back_populates='recipes')
