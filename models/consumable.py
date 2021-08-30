from sqlalchemy.orm import relationship
from models.base import Base
from sqlalchemy import Column
from sqlalchemy.types import Text, Integer, String


class Consumable(Base):
    __tablename__='consumable'
    
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    
    agility = Column(Integer, nullable = True)
    chance = Column(Integer, nullable= True)
    intelligence = Column(Integer, nullable=True)
    strength = Column(Integer, nullable=True)
    wisdom = Column(Integer, nullable=True)
    hp = Column(Integer, nullable = True)
    energy = Column(Integer, nullable= True)
    profession_bonus = Column(Integer, nullable = True)
    xp_bonus = Column(Integer, nullable = True)
    bonus_duration = Column(Integer, nullable = True)
    conditions = Column(Text, nullable=True)
    
    recipe = relationship('Recipe', back_populates='consumable', uselist=False)
    ingredients = relationship('Ingredient', back_populates='consumable')
