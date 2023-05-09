from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from models.base import Base
from sqlalchemy.types import String, Integer
from sqlalchemy import Column
from models.ingredient import Ingredient
from models.equipment import Equipment
from models.weapon import Weapon
from models.consumable import Consumable

# Recipe model class - generates an ID, gathers level the profession takes for the recipe to be crafted and associates it to the correct profession, ingredients, equipment , and weapon
class Recipe(Base):
    __tablename__ = 'recipe'
    #identification
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    level = Column(Integer, nullable=False)
    profession_id = Column(Integer, ForeignKey('profession.id'), nullable = True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'), nullable=True)
    weapon_id = Column(Integer, ForeignKey('weapon.id'), nullable = True)
    consumable_id = Column(Integer, ForeignKey('consumable.id'), nullable = True)
    resource_id = Column(Integer, ForeignKey('resource.id'), nullable = True)
    #relationships - can belong to one equipment or weapon. Many to many relationship with resources (ingredients)
    ingredients = relationship('Ingredient', back_populates='recipe')
    equipment = relationship('Equipment', back_populates='recipes')
    weapon = relationship('Weapon', back_populates='recipes')
    consumable = relationship('Consumable', back_populates='recipes')
    resource = relationship('Resource', back_populates='recipes')
