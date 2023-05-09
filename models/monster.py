from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy import Column, MetaData, String, Boolean
from .monsterresource import MonsterResource
from .monsterequipment import MonsterEquipment
from .monsterharvest import MonsterHarvest
from sqlalchemy.dialects.postgresql import INT4RANGE
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from helpers import db

from .base import Base

# Monster model class - gathers id and basic stats for each monster and associates it to the resources it drops
class Monster(Base):
    __tablename__='monster'
    #Identification fields
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(128),nullable=False)
    family = Column(String(128),nullable=False)
    catchable = Column(Boolean,nullable=False)
    image = Column(String, nullable = False)

    #relationship - resources the monster drops
    equipments = relationship("Equipment", secondary="monster_equipment", back_populates="monsters")
    weapons = relationship("Weapon", secondary="monster_weapon", back_populates="monsters")
    resources = relationship("Resource", secondary="monster_resource", back_populates="monsters")
    harvest = relationship("Resource", secondary="monster_harvest", back_populates="monsters")

    
    level = Column(INT4RANGE, nullable = True)
    pm = Column(Integer, nullable = True)
    pa = Column(Integer, nullable = True)
    pv = Column(Integer, nullable = True)
    initiative = Column(Integer, nullable = True)
    tacle = Column(Integer, nullable = True)
    esquive = Column(Integer, nullable = True)
    parade = Column(Integer, nullable = True)
    critique = Column(Integer, nullable = True)
    maitrise_eau = Column(Integer, nullable = True)
    maitrise_feu = Column(Integer, nullable = True)
    maitrise_terre = Column(Integer, nullable = True)
    maitrise_air = Column(Integer, nullable = True)
    resistance_eau = Column(Integer, nullable = True)
    resistance_feu = Column(Integer, nullable = True)
    resistance_terre = Column(Integer, nullable = True)
    resistance_air = Column(Integer, nullable = True)