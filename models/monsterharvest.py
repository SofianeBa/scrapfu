from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.sql.schema import Column, ForeignKey 
from .base import Base

# MonsterEquipment model class - Used for the Monster and Equipment's many <-> many relationship. Add drop_rate (percentage) to each association
class MonsterHarvest(Base):
    __tablename__='monster_harvest'
    monster_id = Column(ForeignKey('monster.id'), primary_key=True)
    resource_id = Column(ForeignKey('resource.id'), primary_key=True)
    profesion_id = Column(ForeignKey('profesion.id'), primary_key=True)
    profesion_level = Column(Integer, nullable=False)