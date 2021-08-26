from sys import meta_path
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy import Column, String
from .monsterresource import MonsterResource
from sqlalchemy.dialects.postgresql import INT4RANGE
from .base import Base

# Monster model class - gathers id and basic stats for each monster and associates it to the resources it drops
class Monster(Base):
    __tablename__='monster'
    #Identification fields
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(128),nullable=False)
    family = Column(String(128),nullable=False)
    
    level = Column(INT4RANGE, nullable = True)
    mp = Column(INT4RANGE, nullable = True)
    ap = Column(INT4RANGE, nullable = True)
    hp = Column(INT4RANGE, nullable = True)
    earthres = Column(INT4RANGE, nullable = True)
    waterres = Column(INT4RANGE, nullable = True)
    fireres = Column(INT4RANGE, nullable = True)
    airres = Column(INT4RANGE, nullable = True)
    neutralres = Column(INT4RANGE, nullable = True)

    #relationship - resources the monster drops
    resources = relationship("MonsterResource", back_populates="monster")   