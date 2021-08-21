
from sqlalchemy.sql.expression import null
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column
from models.base import Base

#Ingredient model class - Used for recipe and resource's many <-> many relationship. Adds quantity for reach ingredient in the recipe
class Ingredient(Base):
    __tablename__ = 'ingredient'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(ForeignKey('recipe.id'), nullable=False)
    resource_id = Column(ForeignKey('resource.id'), nullable=True)
    equipment_id = Column(ForeignKey('equipment.id'), nullable=True)
    weapon_id = Column(ForeignKey('weapon.id'), nullable=True)
    quantity = Column(Integer, nullable=False)
    recipe = relationship('Recipe',back_populates='ingredients')
    resource = relationship('Resource',back_populates='recipes')
    equipment = relationship('Equipment', back_populates='ingredients')
    weapon = relationship('Weapon', back_populates='ingredients')