from models.ingredient import Ingredient
from sqlalchemy.dialects.postgresql import INT4RANGE
from models.base import Base
from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Integer, Text

#Equiment model class - gathers identification, effects, and associates to crafting recipe
class Equipment(Base):
    __tablename__ = 'equipment'
    #identification
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    type = Column(String, nullable = False)
    level = Column(Integer, nullable = False)
    name = Column(String, nullable = False)
    description = Column(Text, nullable = True)

    vitality = Column(INT4RANGE, nullable=True)
    ap = Column(INT4RANGE, nullable = True)
    ap_parry = Column(INT4RANGE, nullable = True)
    ap_reduction = Column(INT4RANGE, nullable = True)
    agility = Column(INT4RANGE, nullable = True)
    air_damage = Column(INT4RANGE, nullable = True)
    percent_air_res = Column(INT4RANGE, nullable = True)
    chance = Column(INT4RANGE, nullable = True)
    water_damage = Column(INT4RANGE, nullable = True)
    percent_water_res = Column(INT4RANGE, nullable = True)
    prospecting = Column(INT4RANGE, nullable = True)
    intelligence = Column(INT4RANGE, nullable = True)
    fire_damage = Column(INT4RANGE, nullable = True)
    percent_fire_res = Column(INT4RANGE, nullable = True)
    strength = Column(INT4RANGE, nullable = True)
    earth_damage = Column(INT4RANGE, nullable = True)
    percent_earth_res = Column(INT4RANGE, nullable = True)
    pods = Column(INT4RANGE, nullable = True)
    wisdom = Column(INT4RANGE, nullable = True)
    neutral_damage = Column(INT4RANGE, nullable = True)
    percent_neutral_res = Column(INT4RANGE, nullable = True)
    damage = Column(INT4RANGE, nullable = True)
    damage_reflected = Column(INT4RANGE, nullable = True)
    critical_damage = Column(INT4RANGE, nullable = True)
    critical_res = Column(INT4RANGE, nullable = True)
    percent_critical = Column(INT4RANGE, nullable = True)
    pushback_damage = Column(INT4RANGE, nullable = True)
    pushback_res = Column(INT4RANGE, nullable = True)
    dodge = Column(INT4RANGE, nullable = True)
    heals = Column(INT4RANGE, nullable = True)
    initiative = Column(INT4RANGE, nullable = True)
    lock = Column(INT4RANGE, nullable = True)
    mp = Column(INT4RANGE, nullable = True)
    mp_parry = Column(INT4RANGE, nullable = True)
    mp_reduction = Column(INT4RANGE, nullable = True)
    percent_melee_damage = Column(INT4RANGE, nullable = True)
    percent_melee_res = Column(INT4RANGE, nullable = True)
    percent_ranged_damage = Column(INT4RANGE, nullable = True)
    percent_ranged_res = Column(INT4RANGE, nullable = True)
    percent_spell_damage = Column(INT4RANGE, nullable = True)
    percent_weapon_damage = Column(INT4RANGE, nullable = True)
    summons = Column(INT4RANGE, nullable = True)
    trap_damage = Column(INT4RANGE, nullable = True)
    range = Column(INT4RANGE, nullable = True)

    #relationships
    recipe = relationship('Recipe', back_populates='equipment', uselist=False)
    ingredients = relationship('Ingredient', back_populates='equipment')