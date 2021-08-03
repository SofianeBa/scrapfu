from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from models.base import Base
from sqlalchemy.types import String, Integer
from sqlalchemy import Column
from models.ingredient import Ingredient
from models.equipment import Equipment
from models.weapon import Weapon


class Recipe(Base):
    __tablename__ = 'recipe'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    level = Column(Integer, nullable=False)
    profession = Column(String, ForeignKey('profession.id'), nullable = False)
    equipment_id = Column(String, ForeignKey('equipment.id'), nullable=True)
    weapon_id = Column(String, ForeignKey('weapon.id'), nullable = True)
    ingredients = relationship('Ingredient', back_populates='recipe')
    equipment = relationship('Equipment', back_populates='recipe')
    weapon = relationship('Weapon', back_populates='recipe')
