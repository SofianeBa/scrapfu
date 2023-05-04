from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy import Column, String, Boolean
from .monsterresource import MonsterResource
from .monsterequipment import MonsterEquipment
from .monsterharvest import MonsterHarvest
from sqlalchemy.dialects.postgresql import INT4RANGE
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
    
    level = Column(INT4RANGE, nullable = True)
    pm = Column(INT4RANGE, nullable = True)
    pa = Column(INT4RANGE, nullable = True)
    pv = Column(INT4RANGE, nullable = True)
    initiative = Column(INT4RANGE, nullable = True)
    tacle = Column(INT4RANGE, nullable = True)
    esquive = Column(INT4RANGE, nullable = True)
    parade = Column(INT4RANGE, nullable = True)
    critique = Column(INT4RANGE, nullable = True)
    maitrise_eau = Column(INT4RANGE, nullable = True)
    maitrise_feu = Column(INT4RANGE, nullable = True)
    maitrise_terre = Column(INT4RANGE, nullable = True)
    maitrise_air = Column(INT4RANGE, nullable = True)
    resistance_eau = Column(INT4RANGE, nullable = True)
    resistance_feu = Column(INT4RANGE, nullable = True)
    resistance_terre = Column(INT4RANGE, nullable = True)
    resistance_air = Column(INT4RANGE, nullable = True)

    #relationship - resources the monster drops
    resources = relationship("MonsterResource", back_populates="monster") 
    equipments = relationship("MonsterEquipment", back_populates="monster")
    harvest = relationship("MonsterHarvest", back_populates="monster")