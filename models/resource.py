from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, Text, String 
from .base import Base
from .associationtables import monster_resource_table

class Resource(Base):
    __tablename__='resource'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    level = Column(Integer, nullable=False)
    monsters = relationship("Monster", secondary=monster_resource_table, back_populates='resources')
