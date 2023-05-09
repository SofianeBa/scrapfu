from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Float
from sqlalchemy.sql.schema import Column, ForeignKey 
from .base import Base

# MonsterEquipment model class - Used for the Monster and Equipment's many <-> many relationship. Add drop_rate (percentage) to each association
class MonsterEquipment(Base):
    __tablename__='monster_equipment'
    monster_id = Column(ForeignKey('monster.id'), primary_key=True)
    equipment_id = Column(ForeignKey('equipment.id'), primary_key=True) 
    drop_rate = Column(Float, nullable=True)