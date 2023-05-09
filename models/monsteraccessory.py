from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Float
from sqlalchemy.sql.schema import Column, ForeignKey 
from .base import Base

# MonsterAccessory model class - Used for the Monster and Accessory's many <-> many relationship. Add drop_rate (percentage) to each association
class MonsterAccessory(Base):
    __tablename__='monster_accessory'
    monster_id = Column(ForeignKey('monster.id'), primary_key=True)
    accesory_id = Column(ForeignKey('accesory.id'), primary_key=True) 
    drop_rate = Column(Float, nullable=True)