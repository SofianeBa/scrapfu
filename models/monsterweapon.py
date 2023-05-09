from sqlalchemy.sql.sqltypes import Float
from sqlalchemy.sql.schema import Column, ForeignKey 
from .base import Base

# MonsterWeapon model class - Used for the Monster and Weapon's many <-> many relationship. Add drop_rate (percentage) to each association
class MonsterWeapon(Base):
    __tablename__='monster_weapon'
    monster_id = Column(ForeignKey('monster.id'), primary_key=True)
    weapon_id = Column(ForeignKey('weapon.id'), primary_key=True) 
    drop_rate = Column(Float, nullable=True)