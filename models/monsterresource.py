from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Float, Integer
from sqlalchemy.sql.schema import Column, ForeignKey 
from .base import Base

# MonsterResource model class - Used for the Monster and Resource's many <-> many relationship. Add drop_rate (percentage) to each association
class MonsterResource(Base):
    __tablename__='monster_resource'
    id = Column(Integer,primary_key=True,autoincrement=True)
    monster_id = Column(ForeignKey('monster.id'))
    resource_id = Column(ForeignKey('resource.id')) 
    drop_rate = Column(Float, nullable=True)