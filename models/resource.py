import typing
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, Text, String
from .monsterresource import MonsterResource
from .monsterharvest import MonsterHarvest
from .ingredient import Ingredient
from .base import Base

# Resource model class - Gathers id,name,type, and description. Associates resources to monsters that drop it and recipes that use it
class Resource(Base):
    __tablename__='resource'
    id = Column(Integer, primary_key=True, autoincrement=False)
    type = Column(String, nullable=False)   
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    level = Column(Integer, nullable=False)
    image = Column(String, nullable = False)
    rarity = Column(String, nullable = False)

    monsters = relationship("MonsterResource", back_populates="resource")
    recipes = relationship("Ingredient", back_populates="resource")
    harvest = relationship("MonsterHarvest", back_populates="resource") 
    recipe = relationship('Recipe', back_populates='resource')

    def __repr__(self) -> str:
        return self._repr(id=self.id,type=self.type,name=self.name,description=self.description,level=self.level,image=self.image,rarity=self.rarity)

    def _repr(self, **fields: typing.Dict[str, typing.Any]) -> str:
        '''
        Helper for __repr__
        '''
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            try:
                field_strings.append(f'{key}={field!r}')
            except sa.orm.exc.DetachedInstanceError:
                field_strings.append(f'{key}=DetachedInstanceError')
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"