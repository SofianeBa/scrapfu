from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Float
from sqlalchemy.sql.schema import Column, ForeignKey 
from .base import Base

# MonsterResource model class - Used for the Monster and Resource's many <-> many relationship. Add drop_rate (percentage) to each association
class MonsterResource(Base):
    __tablename__='monster_resource'
    monster_id = Column(ForeignKey('monster.id'), primary_key=True)
    resource_id = Column(ForeignKey('resource.id'), primary_key=True) 
    drop_rate = Column(Float, nullable=True)
    monster = relationship('Monster',back_populates='resources')
    resource = relationship('Resource',back_populates='monsters')