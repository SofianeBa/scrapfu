from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.sql.schema import Column, ForeignKey 
from .base import Base

class Mrassociation(Base):
    __tablename__='mrassociation'
    monster_id = Column(ForeignKey('monster.id'), primary_key=True)
    resource_id = Column(ForeignKey('resource.id'), primary_key=True) 
    drop_rate = Column(Integer, nullable=True)
    monster = relationship('Monster',back_populates='resources')
    resource = relationship('Resource',back_populates='monsters')