from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, Text, String
from .mrassociation import Mrassociation
from .base import Base

class Resource(Base):
    __tablename__='resource'
    id = Column(Integer, primary_key=True, autoincrement=False)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    level = Column(Integer, nullable=False)
    monsters = relationship("Mrassociation", back_populates="resource")