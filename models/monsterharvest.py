from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Float, Integer, String
from sqlalchemy.sql.schema import Column, ForeignKey 
from .base import Base

# MonsterEquipment model class - Used for the Monster and Equipment's many <-> many relationship. Add drop_rate (percentage) to each association
class MonsterHarvest(Base):
    __tablename__='monster_harvest'
    monster_id = Column(ForeignKey('monster.id'), primary_key=True)
    resource_id = Column(ForeignKey('resource.id'), primary_key=True)
    job_name = Column(String, nullable=False)
    job_level = Column(Integer, nullable=False)
    monster = relationship('Monster',back_populates='harvest')
    resource = relationship('Resource',back_populates='harvest')